"""Unit tests for simulation data models."""
import pytest
from src.simulation.models import (
    SimulationEvent,
    SimulationSummary,
    ValidationResult,
    DeviceQueueStats,
    OperationStats,
    OperationWaitStats
)


class TestSimulationEvent:
    """Tests for SimulationEvent dataclass."""

    def test_valid_event_creation(self):
        """Test creating a valid simulation event."""
        event = SimulationEvent(
            timestamp=10.5,
            event_type="START",
            sample_id="SAMPLE_001",
            operation_id="op1",
            device_id="dev1",
            duration=5.0,
            wait_time=2.0,
            device_queue_length=1,
            notes="test event"
        )
        assert event.timestamp == 10.5
        assert event.event_type == "START"
        assert event.sample_id == "SAMPLE_001"
        assert event.operation_id == "op1"
        assert event.device_id == "dev1"
        assert event.duration == 5.0
        assert event.wait_time == 2.0
        assert event.device_queue_length == 1
        assert event.notes == "test event"

    def test_event_with_default_notes(self):
        """Test event creation with default empty notes."""
        event = SimulationEvent(
            timestamp=0.0,
            event_type="QUEUED",
            sample_id="SAMPLE_000",
            operation_id="op1",
            device_id="dev1",
            duration=0.0,
            wait_time=0.0,
            device_queue_length=0
        )
        assert event.notes == ""

    def test_negative_timestamp_raises_error(self):
        """Test that negative timestamp raises ValueError."""
        with pytest.raises(ValueError, match="timestamp must be non-negative"):
            SimulationEvent(
                timestamp=-1.0,
                event_type="START",
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=5.0,
                wait_time=0.0,
                device_queue_length=0
            )

    def test_invalid_event_type_raises_error(self):
        """Test that invalid event type raises ValueError."""
        with pytest.raises(ValueError, match="event_type must be one of"):
            SimulationEvent(
                timestamp=0.0,
                event_type="INVALID",
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=5.0,
                wait_time=0.0,
                device_queue_length=0
            )

    def test_valid_event_types(self):
        """Test all valid event types."""
        valid_types = ["QUEUED", "START", "COMPLETE", "RELEASED"]
        for event_type in valid_types:
            event = SimulationEvent(
                timestamp=0.0,
                event_type=event_type,
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=0.0,
                wait_time=0.0,
                device_queue_length=0
            )
            assert event.event_type == event_type

    def test_negative_duration_raises_error(self):
        """Test that negative duration raises ValueError."""
        with pytest.raises(ValueError, match="duration must be non-negative"):
            SimulationEvent(
                timestamp=0.0,
                event_type="START",
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=-5.0,
                wait_time=0.0,
                device_queue_length=0
            )

    def test_negative_wait_time_raises_error(self):
        """Test that negative wait_time raises ValueError."""
        with pytest.raises(ValueError, match="wait_time must be non-negative"):
            SimulationEvent(
                timestamp=0.0,
                event_type="START",
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=5.0,
                wait_time=-1.0,
                device_queue_length=0
            )

    def test_negative_queue_length_raises_error(self):
        """Test that negative queue length raises ValueError."""
        with pytest.raises(ValueError, match="device_queue_length must be non-negative"):
            SimulationEvent(
                timestamp=0.0,
                event_type="START",
                sample_id="SAMPLE_001",
                operation_id="op1",
                device_id="dev1",
                duration=5.0,
                wait_time=0.0,
                device_queue_length=-1
            )


class TestSimulationSummary:
    """Tests for SimulationSummary dataclass."""

    def test_valid_summary_creation(self):
        """Test creating a valid simulation summary."""
        summary = SimulationSummary(
            total_simulation_time=100.0,
            num_samples_completed=5,
            num_samples_failed=0,
            device_utilization={"dev1": 0.85, "dev2": 0.60},
            device_queue_stats={
                "dev1": DeviceQueueStats(max_queue_length=2, avg_queue_time=10.0)
            },
            operation_stats={
                "op1": OperationStats(mean_duration=10.0, sample_count=5)
            },
            operation_wait_times={
                "op1": OperationWaitStats(mean_wait=2.0, total_wait=10.0, wait_events=5)
            },
            total_throughput=0.05,
            mean_sample_cycle_time=20.0,
            min_sample_cycle_time=18.0,
            max_sample_cycle_time=22.0,
            bottleneck_device="dev1",
            bottleneck_utilization=0.85
        )
        assert summary.total_simulation_time == 100.0
        assert summary.num_samples_completed == 5
        assert summary.bottleneck_device == "dev1"

    def test_negative_simulation_time_raises_error(self):
        """Test that negative simulation time raises ValueError."""
        with pytest.raises(ValueError, match="total_simulation_time must be non-negative"):
            SimulationSummary(
                total_simulation_time=-1.0,
                num_samples_completed=5,
                num_samples_failed=0,
                device_utilization={},
                device_queue_stats={},
                operation_stats={},
                operation_wait_times={},
                total_throughput=0.05,
                mean_sample_cycle_time=20.0,
                min_sample_cycle_time=18.0,
                max_sample_cycle_time=22.0,
                bottleneck_device="dev1",
                bottleneck_utilization=0.85
            )

    def test_negative_samples_completed_raises_error(self):
        """Test that negative samples completed raises ValueError."""
        with pytest.raises(ValueError, match="num_samples_completed must be non-negative"):
            SimulationSummary(
                total_simulation_time=100.0,
                num_samples_completed=-1,
                num_samples_failed=0,
                device_utilization={},
                device_queue_stats={},
                operation_stats={},
                operation_wait_times={},
                total_throughput=0.05,
                mean_sample_cycle_time=20.0,
                min_sample_cycle_time=18.0,
                max_sample_cycle_time=22.0,
                bottleneck_device="dev1",
                bottleneck_utilization=0.85
            )

    def test_invalid_utilization_above_one_raises_error(self):
        """Test that utilization > 1.0 raises ValueError."""
        with pytest.raises(ValueError, match="device_utilization.*must be between 0.0 and 1.0"):
            SimulationSummary(
                total_simulation_time=100.0,
                num_samples_completed=5,
                num_samples_failed=0,
                device_utilization={"dev1": 1.5},
                device_queue_stats={},
                operation_stats={},
                operation_wait_times={},
                total_throughput=0.05,
                mean_sample_cycle_time=20.0,
                min_sample_cycle_time=18.0,
                max_sample_cycle_time=22.0,
                bottleneck_device="dev1",
                bottleneck_utilization=0.85
            )

    def test_invalid_utilization_below_zero_raises_error(self):
        """Test that utilization < 0.0 raises ValueError."""
        with pytest.raises(ValueError, match="device_utilization.*must be between 0.0 and 1.0"):
            SimulationSummary(
                total_simulation_time=100.0,
                num_samples_completed=5,
                num_samples_failed=0,
                device_utilization={"dev1": -0.1},
                device_queue_stats={},
                operation_stats={},
                operation_wait_times={},
                total_throughput=0.05,
                mean_sample_cycle_time=20.0,
                min_sample_cycle_time=18.0,
                max_sample_cycle_time=22.0,
                bottleneck_device="dev1",
                bottleneck_utilization=0.85
            )

    def test_valid_utilization_boundary_values(self):
        """Test that utilization at boundaries (0.0 and 1.0) is valid."""
        summary = SimulationSummary(
            total_simulation_time=100.0,
            num_samples_completed=5,
            num_samples_failed=0,
            device_utilization={"dev1": 0.0, "dev2": 1.0},
            device_queue_stats={},
            operation_stats={},
            operation_wait_times={},
            total_throughput=0.05,
            mean_sample_cycle_time=20.0,
            min_sample_cycle_time=18.0,
            max_sample_cycle_time=22.0,
            bottleneck_device="dev1",
            bottleneck_utilization=1.0
        )
        assert summary.device_utilization["dev1"] == 0.0
        assert summary.device_utilization["dev2"] == 1.0


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result_no_errors(self):
        """Test validation result with no errors."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_invalid_result_with_errors(self):
        """Test validation result with errors."""
        result = ValidationResult(
            is_valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"]
        )
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1

    def test_default_empty_lists(self):
        """Test that errors and warnings default to empty lists."""
        result = ValidationResult(is_valid=True)
        assert result.errors == []
        assert result.warnings == []


class TestDeviceQueueStats:
    """Tests for DeviceQueueStats dataclass."""

    def test_default_values(self):
        """Test default values for queue stats."""
        stats = DeviceQueueStats()
        assert stats.max_queue_length == 0
        assert stats.avg_queue_time == 0.0
        assert stats.total_queue_time == 0.0
        assert stats.queue_events == 0

    def test_custom_values(self):
        """Test creating queue stats with custom values."""
        stats = DeviceQueueStats(
            max_queue_length=5,
            avg_queue_time=12.5,
            total_queue_time=50.0,
            queue_events=4
        )
        assert stats.max_queue_length == 5
        assert stats.avg_queue_time == 12.5
        assert stats.total_queue_time == 50.0
        assert stats.queue_events == 4


class TestOperationStats:
    """Tests for OperationStats dataclass."""

    def test_default_values(self):
        """Test default values for operation stats."""
        stats = OperationStats()
        assert stats.mean_duration == 0.0
        assert stats.stdev_duration == 0.0
        assert stats.min_duration == 0.0
        assert stats.max_duration == 0.0
        assert stats.median_duration == 0.0
        assert stats.sample_count == 0

    def test_custom_values(self):
        """Test creating operation stats with custom values."""
        stats = OperationStats(
            mean_duration=10.5,
            stdev_duration=1.2,
            min_duration=8.0,
            max_duration=13.0,
            median_duration=10.0,
            sample_count=100
        )
        assert stats.mean_duration == 10.5
        assert stats.sample_count == 100


class TestOperationWaitStats:
    """Tests for OperationWaitStats dataclass."""

    def test_default_values(self):
        """Test default values for wait stats."""
        stats = OperationWaitStats()
        assert stats.mean_wait == 0.0
        assert stats.total_wait == 0.0
        assert stats.wait_events == 0

    def test_custom_values(self):
        """Test creating wait stats with custom values."""
        stats = OperationWaitStats(
            mean_wait=5.5,
            total_wait=55.0,
            wait_events=10
        )
        assert stats.mean_wait == 5.5
        assert stats.total_wait == 55.0
        assert stats.wait_events == 10
