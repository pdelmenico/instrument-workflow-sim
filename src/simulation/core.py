"""Core simulation engine using SimPy for discrete-event simulation."""
import logging
from typing import Dict, List, Tuple, Any
import simpy
import numpy as np

from src.simulation.models import (
    SimulationEvent,
    SimulationSummary,
    DeviceQueueStats,
    OperationStats,
    OperationWaitStats
)
from src.simulation.timing import sample_timing, set_random_seed


logger = logging.getLogger(__name__)


class SimulationEngine:
    """Orchestrates discrete-event simulation using SimPy.

    The simulation engine manages the execution of workflow simulations,
    including resource allocation, event logging, and statistics computation.

    Attributes:
        workflow: Validated workflow definition dictionary
        scenario: Validated scenario configuration dictionary
        env: SimPy environment for discrete-event simulation
        resources: Dictionary mapping device_id to SimPy Resource
        event_log: List of all simulation events
    """

    def __init__(self, workflow: Dict[str, Any], scenario: Dict[str, Any]) -> None:
        """Initialize simulation engine.

        Args:
            workflow: Validated workflow JSON definition
            scenario: Validated scenario configuration

        Example:
            >>> engine = SimulationEngine(workflow, scenario)
            >>> events, summary = engine.run()
        """
        self.workflow = workflow
        self.scenario = scenario
        self.env = simpy.Environment()
        self.resources: Dict[str, simpy.Resource] = {}
        self.event_log: List[SimulationEvent] = []

        # Track sample completion times for cycle time calculation
        self._sample_start_times: Dict[str, float] = {}
        self._sample_end_times: Dict[str, float] = {}

    def initialize_resources(self) -> None:
        """Create SimPy Resource for each device in workflow.

        Each device becomes a SimPy Resource with capacity specified
        in the workflow definition. This enables automatic queuing
        and resource contention modeling.
        """
        for device in self.workflow['devices']:
            device_id = device['device_id']
            capacity = device['resource_capacity']

            self.resources[device_id] = simpy.Resource(
                self.env,
                capacity=capacity
            )

            logger.debug(f"Initialized resource '{device_id}' with capacity {capacity}")

    def _compute_entry_times(self) -> List[Tuple[str, float]]:
        """Compute sample entry times based on entry pattern.

        Returns:
            List of (sample_id, entry_time) tuples

        Raises:
            ValueError: If pattern type is not supported
        """
        pattern = self.scenario['sample_entry_pattern']
        pattern_type = pattern['pattern_type']
        num_samples = pattern.get('num_samples', 1)

        if pattern_type in ['synchronized', 'single']:
            # All samples enter at time 0
            entry_times = [
                (f"SAMPLE_{i:03d}", 0.0)
                for i in range(num_samples)
            ]
            logger.info(f"Generated {len(entry_times)} sample(s) with {pattern_type} entry pattern")
            return entry_times
        else:
            raise ValueError(
                f"Pattern type '{pattern_type}' not supported in Phase 1a. "
                f"Supported types: synchronized, single"
            )

    def _sample_process(self, sample_id: str, entry_time: float):
        """Generator function for a single sample's workflow execution.

        This coroutine is executed by SimPy and models one sample flowing
        through the entire workflow, competing for device resources with
        other samples.

        Args:
            sample_id: Unique identifier for this sample
            entry_time: Simulation time when sample enters system

        Yields:
            SimPy events (timeouts and resource requests)
        """
        # Wait until entry time
        if entry_time > 0:
            yield self.env.timeout(entry_time)

        # Record sample start time
        self._sample_start_times[sample_id] = self.env.now

        logger.debug(f"{sample_id} entered system at t={self.env.now}")

        # Process each operation in sequence
        for step in self.workflow['base_sequence']:
            operation_id = step['operation_id']

            # Find operation definition
            op_def = next(
                (op for op in self.workflow['operations']
                 if op['operation_id'] == operation_id),
                None
            )

            if not op_def:
                raise ValueError(
                    f"Operation '{operation_id}' not found in workflow definition"
                )

            device_id = op_def['device_id']
            device_resource = self.resources[device_id]

            # Record QUEUED event (before requesting resource)
            queue_len = len(device_resource.queue)
            self.event_log.append(SimulationEvent(
                timestamp=self.env.now,
                event_type="QUEUED",
                sample_id=sample_id,
                operation_id=operation_id,
                device_id=device_id,
                duration=0.0,
                wait_time=0.0,
                device_queue_length=queue_len,
                notes=""
            ))

            # Request device resource
            queue_start_time = self.env.now
            with device_resource.request() as req:
                yield req

                # Calculate wait time
                wait_time = self.env.now - queue_start_time

                # Record START event
                self.event_log.append(SimulationEvent(
                    timestamp=self.env.now,
                    event_type="START",
                    sample_id=sample_id,
                    operation_id=operation_id,
                    device_id=device_id,
                    duration=0.0,
                    wait_time=wait_time,
                    device_queue_length=0,
                    notes=""
                ))

                logger.debug(
                    f"{sample_id} started '{operation_id}' on '{device_id}' "
                    f"at t={self.env.now} (waited {wait_time:.2f}s)"
                )

                # Sample operation duration
                duration = sample_timing(op_def['timing'])

                # Execute operation (wait for duration)
                yield self.env.timeout(duration)

                # Record COMPLETE event
                self.event_log.append(SimulationEvent(
                    timestamp=self.env.now,
                    event_type="COMPLETE",
                    sample_id=sample_id,
                    operation_id=operation_id,
                    device_id=device_id,
                    duration=duration,
                    wait_time=wait_time,
                    device_queue_length=0,
                    notes=""
                ))

                logger.debug(
                    f"{sample_id} completed '{operation_id}' on '{device_id}' "
                    f"at t={self.env.now} (duration {duration:.2f}s)"
                )

        # Record sample end time
        self._sample_end_times[sample_id] = self.env.now
        logger.info(f"{sample_id} completed workflow at t={self.env.now}")

    def run(self) -> Tuple[List[SimulationEvent], SimulationSummary]:
        """Execute simulation and return event log and summary statistics.

        This is the main entry point for running a simulation. It orchestrates
        the entire simulation lifecycle:
        1. Set random seed (if provided)
        2. Initialize resources
        3. Compute sample entry times
        4. Start sample processes
        5. Run SimPy simulation
        6. Compute summary statistics

        Returns:
            Tuple of (event_log, summary):
                - event_log: List of all simulation events
                - summary: SimulationSummary with statistics

        Example:
            >>> engine = SimulationEngine(workflow, scenario)
            >>> events, summary = engine.run()
            >>> print(f"Completed {summary.num_samples_completed} samples")
        """
        # Set random seed for reproducibility
        sim_config = self.scenario.get('simulation_config', {})
        random_seed = sim_config.get('random_seed')
        if random_seed is not None:
            set_random_seed(random_seed)
            logger.info(f"Set random seed to {random_seed}")

        # Initialize resources
        self.initialize_resources()

        # Compute sample entry times
        entry_times = self._compute_entry_times()

        # Start sample process for each sample
        for sample_id, entry_time in entry_times:
            self.env.process(self._sample_process(sample_id, entry_time))

        # Run simulation
        max_time = sim_config.get('max_simulation_time')
        if max_time:
            logger.info(f"Starting simulation (max time: {max_time}s)")
            self.env.run(until=max_time)
        else:
            logger.info("Starting simulation (no time limit)")
            self.env.run()  # Run until all processes complete

        logger.info(
            f"Simulation complete. Processed {len(self.event_log)} events "
            f"in {self.env.now:.2f}s simulation time"
        )

        # Compute summary statistics
        summary = self._compute_summary()

        return self.event_log, summary

    def _compute_summary(self) -> SimulationSummary:
        """Compute summary statistics from event log.

        This is a stub implementation for Week 2. Week 3 will implement
        full statistics computation including:
        - Device utilization
        - Queue statistics
        - Operation duration statistics
        - Bottleneck identification

        Returns:
            SimulationSummary with basic statistics
        """
        # Basic statistics for Week 2
        total_time = self.env.now
        num_completed = len(self._sample_end_times)
        num_failed = 0

        # Calculate sample cycle times
        cycle_times = []
        for sample_id in self._sample_end_times:
            if sample_id in self._sample_start_times:
                cycle_time = self._sample_end_times[sample_id] - self._sample_start_times[sample_id]
                cycle_times.append(cycle_time)

        mean_cycle_time = np.mean(cycle_times) if cycle_times else 0.0
        min_cycle_time = np.min(cycle_times) if cycle_times else 0.0
        max_cycle_time = np.max(cycle_times) if cycle_times else 0.0

        throughput = num_completed / total_time if total_time > 0 else 0.0

        # Stub data structures (will be computed properly in Week 3)
        device_utilization = {
            device['device_id']: 0.0
            for device in self.workflow['devices']
        }

        device_queue_stats = {
            device['device_id']: DeviceQueueStats()
            for device in self.workflow['devices']
        }

        operation_stats = {
            op['operation_id']: OperationStats()
            for op in self.workflow['operations']
        }

        operation_wait_times = {
            op['operation_id']: OperationWaitStats()
            for op in self.workflow['operations']
        }

        # Simple bottleneck identification (first device for now)
        bottleneck_device = self.workflow['devices'][0]['device_id'] if self.workflow['devices'] else ""

        summary = SimulationSummary(
            total_simulation_time=total_time,
            num_samples_completed=num_completed,
            num_samples_failed=num_failed,
            device_utilization=device_utilization,
            device_queue_stats=device_queue_stats,
            operation_stats=operation_stats,
            operation_wait_times=operation_wait_times,
            total_throughput=throughput,
            mean_sample_cycle_time=mean_cycle_time,
            min_sample_cycle_time=min_cycle_time,
            max_sample_cycle_time=max_cycle_time,
            bottleneck_device=bottleneck_device,
            bottleneck_utilization=0.0
        )

        logger.info(
            f"Summary: {num_completed} samples completed in {total_time:.2f}s "
            f"(throughput: {throughput:.6f} samples/sec)"
        )

        return summary
