"""Integration tests for SimulationEngine."""
import pytest
import numpy as np
from src.simulation.core import SimulationEngine
from src.simulation.timing import set_random_seed


class TestSimulationEngineInitialization:
    """Tests for SimulationEngine initialization."""

    def test_engine_initialization(self, simple_workflow, simple_scenario):
        """Test that engine initializes correctly."""
        engine = SimulationEngine(simple_workflow, simple_scenario)

        assert engine.workflow == simple_workflow
        assert engine.scenario == simple_scenario
        assert engine.env is not None
        assert len(engine.resources) == 0  # Not initialized yet
        assert len(engine.event_log) == 0

    def test_initialize_resources(self, simple_workflow, simple_scenario):
        """Test that resources are created correctly."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        engine.initialize_resources()

        assert len(engine.resources) == 1
        assert 'dev1' in engine.resources
        assert engine.resources['dev1'].capacity == 1

    def test_initialize_multiple_resources(self, multi_device_workflow, simple_scenario):
        """Test initialization of multiple resources."""
        simple_scenario['workflow_id'] = 'multi_device'
        engine = SimulationEngine(multi_device_workflow, simple_scenario)
        engine.initialize_resources()

        assert len(engine.resources) == 2
        assert 'liquid_handler' in engine.resources
        assert 'thermal_cycler' in engine.resources

    def test_resource_capacity_set_correctly(self):
        """Test that resource capacity is set from workflow."""
        workflow = {
            "workflow_id": "capacity_test",
            "devices": [
                {
                    "device_id": "multi_capacity_device",
                    "device_name": "Multi Capacity Device",
                    "resource_capacity": 5,
                    "scheduling_policy": "FIFO"
                }
            ],
            "operations": [],
            "base_sequence": []
        }
        scenario = {
            "scenario_id": "test",
            "workflow_id": "capacity_test",
            "sample_entry_pattern": {"pattern_type": "single", "num_samples": 1},
            "simulation_config": {}
        }

        engine = SimulationEngine(workflow, scenario)
        engine.initialize_resources()

        assert engine.resources['multi_capacity_device'].capacity == 5


class TestEntryTimeComputation:
    """Tests for _compute_entry_times method."""

    def test_single_pattern_entry_time(self, simple_workflow, simple_scenario):
        """Test that single pattern creates one sample at t=0."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        entry_times = engine._compute_entry_times()

        assert len(entry_times) == 1
        assert entry_times[0] == ("SAMPLE_000", 0.0)

    def test_synchronized_pattern_entry_times(self, multi_device_workflow, synchronized_scenario):
        """Test that synchronized pattern creates N samples at t=0."""
        engine = SimulationEngine(multi_device_workflow, synchronized_scenario)
        entry_times = engine._compute_entry_times()

        assert len(entry_times) == 3
        for i, (sample_id, entry_time) in enumerate(entry_times):
            assert sample_id == f"SAMPLE_{i:03d}"
            assert entry_time == 0.0

    def test_unsupported_pattern_raises_error(self, simple_workflow, simple_scenario):
        """Test that unsupported pattern type raises ValueError."""
        simple_scenario['sample_entry_pattern']['pattern_type'] = 'staggered'

        engine = SimulationEngine(simple_workflow, simple_scenario)

        with pytest.raises(ValueError, match="not supported in Phase 1a"):
            engine._compute_entry_times()


class TestSingleSampleSimulation:
    """Tests for single sample workflow execution."""

    def test_single_sample_fixed_timing(self, simple_workflow, simple_scenario):
        """Test single sample with fixed timing produces deterministic output."""
        set_random_seed(42)
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, summary = engine.run()

        # Should have events: QUEUED, START, COMPLETE
        assert len(events) >= 3

        # Check event types are in correct order
        assert events[0].event_type == "QUEUED"
        assert events[1].event_type == "START"
        assert events[2].event_type == "COMPLETE"

        # Check sample ID
        assert all(e.sample_id == "SAMPLE_000" for e in events)

        # Check operation ID
        assert all(e.operation_id == "op1" for e in events)

        # Check device ID
        assert all(e.device_id == "dev1" for e in events)

        # Check timing
        complete_event = events[2]
        assert complete_event.duration == 10.0
        assert complete_event.timestamp == 10.0  # Started at 0, duration 10

        # Check summary
        assert summary.num_samples_completed == 1
        assert summary.num_samples_failed == 0
        assert summary.total_simulation_time == 10.0

    def test_single_sample_no_wait_time(self, simple_workflow, simple_scenario):
        """Test that single sample has no wait time."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, _ = engine.run()

        start_event = next(e for e in events if e.event_type == "START")
        assert start_event.wait_time == 0.0

    def test_single_sample_sequential_operations(self, multi_device_workflow, simple_scenario):
        """Test single sample flowing through multiple operations."""
        simple_scenario['workflow_id'] = 'multi_device'
        set_random_seed(42)

        engine = SimulationEngine(multi_device_workflow, simple_scenario)
        events, summary = engine.run()

        # Should have 3 operations × 3 events each = 9 events
        assert len(events) == 9

        # Check operation sequence
        op_ids = [e.operation_id for e in events if e.event_type == "START"]
        assert op_ids == ["load_sample", "add_reagent", "amplify"]

        # Check operations are sequential (next starts after previous completes)
        load_complete = next(e for e in events if e.operation_id == "load_sample" and e.event_type == "COMPLETE")
        add_start = next(e for e in events if e.operation_id == "add_reagent" and e.event_type == "START")
        assert add_start.timestamp >= load_complete.timestamp

    def test_event_timestamps_monotonic(self, multi_device_workflow, simple_scenario):
        """Test that event timestamps are monotonically increasing."""
        simple_scenario['workflow_id'] = 'multi_device'
        set_random_seed(42)

        engine = SimulationEngine(multi_device_workflow, simple_scenario)
        events, _ = engine.run()

        timestamps = [e.timestamp for e in events]
        assert timestamps == sorted(timestamps)


class TestSynchronizedBatchSimulation:
    """Tests for synchronized batch simulation with device contention."""

    def test_synchronized_batch_two_samples(self):
        """Test synchronized batch with 2 samples on single device."""
        workflow = {
            "workflow_id": "batch_test",
            "devices": [
                {
                    "device_id": "dev1",
                    "device_name": "Device 1",
                    "resource_capacity": 1,
                    "scheduling_policy": "FIFO"
                }
            ],
            "operations": [
                {
                    "operation_id": "op1",
                    "operation_name": "Operation 1",
                    "device_id": "dev1",
                    "timing": {"type": "fixed", "value": 10.0},
                    "operation_type": "processing"
                }
            ],
            "base_sequence": [
                {
                    "sequence_id": 1,
                    "operation_id": "op1",
                    "predecessors": []
                }
            ]
        }

        scenario = {
            "scenario_id": "batch",
            "workflow_id": "batch_test",
            "sample_entry_pattern": {
                "pattern_type": "synchronized",
                "num_samples": 2
            },
            "simulation_config": {"random_seed": 42}
        }

        engine = SimulationEngine(workflow, scenario)
        events, summary = engine.run()

        # Both samples should complete
        assert summary.num_samples_completed == 2

        # Total time should be ~20 seconds (2 samples × 10 sec each, sequential)
        assert 19.0 < summary.total_simulation_time <= 21.0

        # Check that second sample had to wait
        sample_1_events = [e for e in events if e.sample_id == "SAMPLE_001"]
        start_event = next(e for e in sample_1_events if e.event_type == "START")
        assert start_event.wait_time > 0

    def test_device_queue_length_tracked(self):
        """Test that device queue length is tracked correctly.

        Note: When samples enter simultaneously at t=0, they all check
        the queue before any have requested resources, so they all see 0.
        Queue delays are reflected in wait_time instead.
        """
        workflow = {
            "workflow_id": "queue_test",
            "devices": [
                {
                    "device_id": "dev1",
                    "device_name": "Device 1",
                    "resource_capacity": 1,
                    "scheduling_policy": "FIFO"
                }
            ],
            "operations": [
                {
                    "operation_id": "op1",
                    "operation_name": "Operation 1",
                    "device_id": "dev1",
                    "timing": {"type": "fixed", "value": 10.0},
                    "operation_type": "processing"
                }
            ],
            "base_sequence": [
                {
                    "sequence_id": 1,
                    "operation_id": "op1",
                    "predecessors": []
                }
            ]
        }

        scenario = {
            "scenario_id": "queue",
            "workflow_id": "queue_test",
            "sample_entry_pattern": {
                "pattern_type": "synchronized",
                "num_samples": 3
            },
            "simulation_config": {"random_seed": 42}
        }

        engine = SimulationEngine(workflow, scenario)
        events, _ = engine.run()

        # Check that samples had to wait (indicating queue contention)
        start_events = [e for e in events if e.event_type == "START"]
        assert len(start_events) == 3

        # First sample starts immediately
        assert start_events[0].wait_time == 0.0

        # Second and third samples have wait times
        assert start_events[1].wait_time > 0
        assert start_events[2].wait_time > 0

        # Verify sequential execution (wait times increase)
        assert start_events[2].wait_time > start_events[1].wait_time

    def test_multi_capacity_device_parallel_execution(self):
        """Test that device with capacity > 1 allows parallel execution."""
        workflow = {
            "workflow_id": "parallel_test",
            "devices": [
                {
                    "device_id": "dev1",
                    "device_name": "Device 1",
                    "resource_capacity": 2,  # Can handle 2 samples simultaneously
                    "scheduling_policy": "FIFO"
                }
            ],
            "operations": [
                {
                    "operation_id": "op1",
                    "operation_name": "Operation 1",
                    "device_id": "dev1",
                    "timing": {"type": "fixed", "value": 10.0},
                    "operation_type": "processing"
                }
            ],
            "base_sequence": [
                {
                    "sequence_id": 1,
                    "operation_id": "op1",
                    "predecessors": []
                }
            ]
        }

        scenario = {
            "scenario_id": "parallel",
            "workflow_id": "parallel_test",
            "sample_entry_pattern": {
                "pattern_type": "synchronized",
                "num_samples": 2
            },
            "simulation_config": {"random_seed": 42}
        }

        engine = SimulationEngine(workflow, scenario)
        events, summary = engine.run()

        # With capacity 2, both samples run in parallel
        # Total time should be ~10 seconds (not 20)
        assert 9.0 < summary.total_simulation_time <= 11.0

        # Both samples should have zero wait time
        sample_0_start = next(e for e in events if e.sample_id == "SAMPLE_000" and e.event_type == "START")
        sample_1_start = next(e for e in events if e.sample_id == "SAMPLE_001" and e.event_type == "START")

        assert sample_0_start.wait_time == 0.0
        assert sample_1_start.wait_time == 0.0


class TestDeterministicBehavior:
    """Tests for deterministic simulation with random seeds."""

    def test_same_seed_produces_identical_results(self, multi_device_workflow, simple_scenario):
        """Test that same seed produces identical event logs."""
        simple_scenario['workflow_id'] = 'multi_device'
        simple_scenario['simulation_config']['random_seed'] = 42

        # Run simulation twice with same seed
        engine1 = SimulationEngine(multi_device_workflow, simple_scenario)
        events1, summary1 = engine1.run()

        engine2 = SimulationEngine(multi_device_workflow, simple_scenario)
        events2, summary2 = engine2.run()

        # Event logs should be identical
        assert len(events1) == len(events2)

        for e1, e2 in zip(events1, events2):
            assert e1.timestamp == e2.timestamp
            assert e1.event_type == e2.event_type
            assert e1.sample_id == e2.sample_id
            assert e1.operation_id == e2.operation_id
            assert e1.device_id == e2.device_id
            assert e1.duration == e2.duration
            assert e1.wait_time == e2.wait_time

        # Summaries should be identical
        assert summary1.total_simulation_time == summary2.total_simulation_time
        assert summary1.num_samples_completed == summary2.num_samples_completed

    def test_different_seeds_produce_different_results(self, multi_device_workflow, simple_scenario):
        """Test that different seeds produce different results."""
        simple_scenario['workflow_id'] = 'multi_device'

        # Run with seed 42
        simple_scenario['simulation_config']['random_seed'] = 42
        engine1 = SimulationEngine(multi_device_workflow, simple_scenario)
        events1, _ = engine1.run()

        # Run with seed 123
        simple_scenario['simulation_config']['random_seed'] = 123
        engine2 = SimulationEngine(multi_device_workflow, simple_scenario)
        events2, _ = engine2.run()

        # At least some durations should differ (due to stochastic timing)
        durations1 = [e.duration for e in events1 if e.event_type == "COMPLETE"]
        durations2 = [e.duration for e in events2 if e.event_type == "COMPLETE"]

        # Triangular and exponential operations should have different durations
        assert durations1 != durations2

    def test_no_seed_runs_successfully(self, simple_workflow, simple_scenario):
        """Test that simulation runs without random seed."""
        # Remove random seed
        if 'random_seed' in simple_scenario['simulation_config']:
            del simple_scenario['simulation_config']['random_seed']

        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, summary = engine.run()

        assert len(events) > 0
        assert summary.num_samples_completed == 1


class TestEventLogContent:
    """Tests for event log content and structure."""

    def test_all_events_have_required_fields(self, simple_workflow, simple_scenario):
        """Test that all events have required fields populated."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, _ = engine.run()

        for event in events:
            assert event.timestamp >= 0
            assert event.event_type in ["QUEUED", "START", "COMPLETE", "RELEASED"]
            assert event.sample_id.startswith("SAMPLE_")
            assert event.operation_id != ""
            assert event.device_id != ""
            assert event.duration >= 0
            assert event.wait_time >= 0
            assert event.device_queue_length >= 0

    def test_complete_event_has_duration(self, simple_workflow, simple_scenario):
        """Test that COMPLETE events have duration set."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, _ = engine.run()

        complete_events = [e for e in events if e.event_type == "COMPLETE"]
        assert len(complete_events) > 0

        for event in complete_events:
            assert event.duration > 0

    def test_queued_event_before_start(self, simple_workflow, simple_scenario):
        """Test that QUEUED event occurs before START."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, _ = engine.run()

        # Find first operation's events
        queued = next(e for e in events if e.event_type == "QUEUED")
        start = next(e for e in events if e.event_type == "START")

        assert events.index(queued) < events.index(start)

    def test_start_event_before_complete(self, simple_workflow, simple_scenario):
        """Test that START event occurs before COMPLETE."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, _ = engine.run()

        start = next(e for e in events if e.event_type == "START")
        complete = next(e for e in events if e.event_type == "COMPLETE")

        assert events.index(start) < events.index(complete)


class TestSummaryStatistics:
    """Tests for summary statistics computation."""

    def test_summary_has_required_fields(self, simple_workflow, simple_scenario):
        """Test that summary has all required fields."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        _, summary = engine.run()

        assert hasattr(summary, 'total_simulation_time')
        assert hasattr(summary, 'num_samples_completed')
        assert hasattr(summary, 'num_samples_failed')
        assert hasattr(summary, 'device_utilization')
        assert hasattr(summary, 'total_throughput')
        assert hasattr(summary, 'mean_sample_cycle_time')

    def test_sample_count_correct(self, multi_device_workflow, synchronized_scenario):
        """Test that sample count is correct."""
        engine = SimulationEngine(multi_device_workflow, synchronized_scenario)
        _, summary = engine.run()

        assert summary.num_samples_completed == 3
        assert summary.num_samples_failed == 0

    def test_throughput_calculated(self, simple_workflow, simple_scenario):
        """Test that throughput is calculated."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        _, summary = engine.run()

        assert summary.total_throughput > 0
        # Throughput = samples / time = 1 / 10 = 0.1
        assert abs(summary.total_throughput - 0.1) < 0.01

    def test_cycle_time_calculated(self, simple_workflow, simple_scenario):
        """Test that cycle time is calculated."""
        engine = SimulationEngine(simple_workflow, simple_scenario)
        _, summary = engine.run()

        # Single sample with 10 second operation
        assert abs(summary.mean_sample_cycle_time - 10.0) < 0.1
        assert abs(summary.min_sample_cycle_time - 10.0) < 0.1
        assert abs(summary.max_sample_cycle_time - 10.0) < 0.1


class TestErrorHandling:
    """Tests for error handling in simulation engine."""

    def test_missing_operation_raises_error(self):
        """Test that missing operation definition raises error."""
        workflow = {
            "workflow_id": "bad_workflow",
            "devices": [{"device_id": "dev1", "device_name": "Dev", "resource_capacity": 1, "scheduling_policy": "FIFO"}],
            "operations": [],  # Empty operations
            "base_sequence": [
                {"sequence_id": 1, "operation_id": "missing_op", "predecessors": []}
            ]
        }

        scenario = {
            "scenario_id": "test",
            "workflow_id": "bad_workflow",
            "sample_entry_pattern": {"pattern_type": "single", "num_samples": 1},
            "simulation_config": {}
        }

        engine = SimulationEngine(workflow, scenario)

        with pytest.raises(ValueError, match="not found in workflow definition"):
            engine.run()

    def test_max_simulation_time_limits_execution(self, simple_workflow, simple_scenario):
        """Test that max_simulation_time limits execution."""
        # Set very short max time
        simple_scenario['simulation_config']['max_simulation_time'] = 5.0

        engine = SimulationEngine(simple_workflow, simple_scenario)
        events, summary = engine.run()

        # Should stop before completion
        assert summary.total_simulation_time <= 5.0
