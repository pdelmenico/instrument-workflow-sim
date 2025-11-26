"""Shared pytest fixtures for testing."""
import pytest
from typing import Dict, Any


@pytest.fixture
def simple_workflow() -> Dict[str, Any]:
    """Minimal valid workflow with one device and one operation."""
    return {
        "workflow_id": "test_simple",
        "workflow_name": "Simple Test Workflow",
        "devices": [
            {
                "device_id": "dev1",
                "device_name": "Test Device",
                "resource_capacity": 1,
                "scheduling_policy": "FIFO"
            }
        ],
        "operations": [
            {
                "operation_id": "op1",
                "operation_name": "Test Operation",
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


@pytest.fixture
def multi_device_workflow() -> Dict[str, Any]:
    """Workflow with multiple devices and sequential operations."""
    return {
        "workflow_id": "multi_device",
        "workflow_name": "Multi Device Workflow",
        "devices": [
            {
                "device_id": "liquid_handler",
                "device_name": "Liquid Handler",
                "resource_capacity": 1,
                "scheduling_policy": "FIFO"
            },
            {
                "device_id": "thermal_cycler",
                "device_name": "Thermal Cycler",
                "resource_capacity": 1,
                "scheduling_policy": "FIFO"
            }
        ],
        "operations": [
            {
                "operation_id": "load_sample",
                "operation_name": "Load Sample",
                "device_id": "liquid_handler",
                "timing": {"type": "fixed", "value": 5.0},
                "operation_type": "setup"
            },
            {
                "operation_id": "add_reagent",
                "operation_name": "Add Reagent",
                "device_id": "liquid_handler",
                "timing": {"type": "triangular", "min": 8.0, "mode": 10.0, "max": 12.0},
                "operation_type": "processing"
            },
            {
                "operation_id": "amplify",
                "operation_name": "PCR Amplification",
                "device_id": "thermal_cycler",
                "timing": {"type": "exponential", "mean": 3600.0},
                "operation_type": "processing"
            }
        ],
        "base_sequence": [
            {
                "sequence_id": 1,
                "operation_id": "load_sample",
                "predecessors": []
            },
            {
                "sequence_id": 2,
                "operation_id": "add_reagent",
                "predecessors": ["load_sample"]
            },
            {
                "sequence_id": 3,
                "operation_id": "amplify",
                "predecessors": ["add_reagent"]
            }
        ]
    }


@pytest.fixture
def simple_scenario() -> Dict[str, Any]:
    """Minimal valid scenario for single sample."""
    return {
        "scenario_id": "test_scenario",
        "scenario_name": "Test Scenario",
        "workflow_id": "test_simple",
        "sample_entry_pattern": {
            "pattern_type": "single",
            "num_samples": 1
        },
        "simulation_config": {
            "random_seed": 42,
            "max_simulation_time": 1000.0
        }
    }


@pytest.fixture
def synchronized_scenario() -> Dict[str, Any]:
    """Scenario with synchronized batch of samples."""
    return {
        "scenario_id": "sync_batch",
        "scenario_name": "Synchronized Batch",
        "workflow_id": "multi_device",
        "sample_entry_pattern": {
            "pattern_type": "synchronized",
            "num_samples": 3
        },
        "simulation_config": {
            "random_seed": 123,
            "max_simulation_time": 7200.0
        }
    }


@pytest.fixture
def workflow_with_cycle() -> Dict[str, Any]:
    """Invalid workflow with circular dependency."""
    return {
        "workflow_id": "circular",
        "workflow_name": "Circular Workflow",
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
                "operation_id": "op_a",
                "operation_name": "Operation A",
                "device_id": "dev1",
                "timing": {"type": "fixed", "value": 10.0},
                "operation_type": "processing"
            },
            {
                "operation_id": "op_b",
                "operation_name": "Operation B",
                "device_id": "dev1",
                "timing": {"type": "fixed", "value": 10.0},
                "operation_type": "processing"
            }
        ],
        "base_sequence": [
            {
                "sequence_id": 1,
                "operation_id": "op_a",
                "predecessors": ["op_b"]
            },
            {
                "sequence_id": 2,
                "operation_id": "op_b",
                "predecessors": ["op_a"]
            }
        ]
    }


@pytest.fixture
def workflow_missing_device_ref() -> Dict[str, Any]:
    """Invalid workflow with missing device reference."""
    return {
        "workflow_id": "bad_ref",
        "workflow_name": "Bad Device Reference",
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
                "device_id": "dev_missing",
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


@pytest.fixture
def workflow_invalid_timing() -> Dict[str, Any]:
    """Invalid workflow with bad timing parameters."""
    return {
        "workflow_id": "bad_timing",
        "workflow_name": "Bad Timing",
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
                "timing": {"type": "triangular", "min": 10.0, "mode": 5.0, "max": 15.0},
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
