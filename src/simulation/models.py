"""Data models for simulation events and summary statistics."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SimulationEvent:
    """Represents a single event in the simulation timeline.

    Attributes:
        timestamp: Simulation clock time in seconds
        event_type: Type of event (QUEUED, START, COMPLETE, RELEASED)
        sample_id: Identifier for the sample
        operation_id: Identifier for the operation being performed
        device_id: Identifier for the device being used
        duration: Actual sampled duration in seconds
        wait_time: Time spent waiting for device in seconds
        device_queue_length: Length of device queue when operation started
        notes: Optional context or additional information
    """
    timestamp: float
    event_type: str
    sample_id: str
    operation_id: str
    device_id: str
    duration: float
    wait_time: float
    device_queue_length: int
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate event data after initialization."""
        if self.timestamp < 0:
            raise ValueError(f"timestamp must be non-negative, got {self.timestamp}")

        if self.event_type not in ["QUEUED", "START", "COMPLETE", "RELEASED"]:
            raise ValueError(f"event_type must be one of QUEUED, START, COMPLETE, RELEASED, got {self.event_type}")

        if self.duration < 0:
            raise ValueError(f"duration must be non-negative, got {self.duration}")

        if self.wait_time < 0:
            raise ValueError(f"wait_time must be non-negative, got {self.wait_time}")

        if self.device_queue_length < 0:
            raise ValueError(f"device_queue_length must be non-negative, got {self.device_queue_length}")


@dataclass
class DeviceQueueStats:
    """Statistics for device queue behavior.

    Attributes:
        max_queue_length: Maximum number of samples waiting
        avg_queue_time: Average time samples spent waiting in seconds
        total_queue_time: Total time across all queue events in seconds
        queue_events: Number of times samples had to queue
    """
    max_queue_length: int = 0
    avg_queue_time: float = 0.0
    total_queue_time: float = 0.0
    queue_events: int = 0


@dataclass
class OperationStats:
    """Statistics for operation execution.

    Attributes:
        mean_duration: Average operation duration in seconds
        stdev_duration: Standard deviation of duration
        min_duration: Minimum observed duration
        max_duration: Maximum observed duration
        median_duration: Median duration
        sample_count: Number of samples that completed this operation
    """
    mean_duration: float = 0.0
    stdev_duration: float = 0.0
    min_duration: float = 0.0
    max_duration: float = 0.0
    median_duration: float = 0.0
    sample_count: int = 0


@dataclass
class OperationWaitStats:
    """Statistics for operation wait times.

    Attributes:
        mean_wait: Average wait time in seconds
        total_wait: Total wait time across all events
        wait_events: Number of times samples had to wait
    """
    mean_wait: float = 0.0
    total_wait: float = 0.0
    wait_events: int = 0


@dataclass
class SimulationSummary:
    """Summary statistics from a completed simulation.

    Attributes:
        total_simulation_time: Total elapsed simulation time in seconds
        num_samples_completed: Number of samples that completed workflow
        num_samples_failed: Number of samples that failed or timed out
        device_utilization: Device utilization percentage (0.0 to 1.0) per device
        device_queue_stats: Queue statistics per device
        operation_stats: Execution statistics per operation
        operation_wait_times: Wait time statistics per operation
        total_throughput: Samples completed per second
        mean_sample_cycle_time: Average time from entry to exit
        min_sample_cycle_time: Minimum sample cycle time
        max_sample_cycle_time: Maximum sample cycle time
        bottleneck_device: Device with highest utilization
        bottleneck_utilization: Utilization of bottleneck device
        bottleneck_queue_delay: Average queue delay at bottleneck
    """
    total_simulation_time: float
    num_samples_completed: int
    num_samples_failed: int
    device_utilization: Dict[str, float]
    device_queue_stats: Dict[str, DeviceQueueStats]
    operation_stats: Dict[str, OperationStats]
    operation_wait_times: Dict[str, OperationWaitStats]
    total_throughput: float
    mean_sample_cycle_time: float
    min_sample_cycle_time: float
    max_sample_cycle_time: float
    bottleneck_device: str
    bottleneck_utilization: float
    bottleneck_queue_delay: float = 0.0

    def __post_init__(self) -> None:
        """Validate summary data after initialization."""
        if self.total_simulation_time < 0:
            raise ValueError(f"total_simulation_time must be non-negative, got {self.total_simulation_time}")

        if self.num_samples_completed < 0:
            raise ValueError(f"num_samples_completed must be non-negative, got {self.num_samples_completed}")

        if self.num_samples_failed < 0:
            raise ValueError(f"num_samples_failed must be non-negative, got {self.num_samples_failed}")

        if self.total_throughput < 0:
            raise ValueError(f"total_throughput must be non-negative, got {self.total_throughput}")

        # Validate utilization values are between 0 and 1
        for device_id, util in self.device_utilization.items():
            if not 0.0 <= util <= 1.0:
                raise ValueError(f"device_utilization for {device_id} must be between 0.0 and 1.0, got {util}")


@dataclass
class ValidationResult:
    """Result of workflow or scenario validation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of error messages (empty if valid)
        warnings: List of warning messages (may exist even if valid)
    """
    is_valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
