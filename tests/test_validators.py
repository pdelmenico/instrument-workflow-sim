"""Unit tests for workflow and scenario validators."""
import pytest
from src.simulation.validators import WorkflowValidator, ScenarioValidator


class TestWorkflowValidator:
    """Tests for WorkflowValidator."""

    def test_valid_simple_workflow(self, simple_workflow):
        """Test that a valid simple workflow passes validation."""
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_valid_multi_device_workflow(self, multi_device_workflow):
        """Test that a valid multi-device workflow passes validation."""
        validator = WorkflowValidator()
        result = validator.validate(multi_device_workflow)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_workflow_id(self, simple_workflow):
        """Test that missing workflow_id is caught."""
        del simple_workflow["workflow_id"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("workflow_id" in err for err in result.errors)

    def test_missing_devices_field(self, simple_workflow):
        """Test that missing devices field is caught."""
        del simple_workflow["devices"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("devices" in err for err in result.errors)

    def test_missing_operations_field(self, simple_workflow):
        """Test that missing operations field is caught."""
        del simple_workflow["operations"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("operations" in err for err in result.errors)

    def test_missing_base_sequence_field(self, simple_workflow):
        """Test that missing base_sequence field is caught."""
        del simple_workflow["base_sequence"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("base_sequence" in err for err in result.errors)

    def test_devices_not_list(self, simple_workflow):
        """Test that devices must be a list."""
        simple_workflow["devices"] = "not a list"
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("devices" in err and "list" in err for err in result.errors)

    def test_empty_devices_list(self, simple_workflow):
        """Test that empty devices list is caught."""
        simple_workflow["devices"] = []
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("at least one device" in err for err in result.errors)

    def test_device_missing_device_id(self, simple_workflow):
        """Test that device missing device_id is caught."""
        del simple_workflow["devices"][0]["device_id"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("device_id" in err for err in result.errors)

    def test_empty_operations_list(self, simple_workflow):
        """Test that empty operations list is caught."""
        simple_workflow["operations"] = []
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("at least one operation" in err for err in result.errors)

    def test_operation_missing_operation_id(self, simple_workflow):
        """Test that operation missing operation_id is caught."""
        del simple_workflow["operations"][0]["operation_id"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("operation_id" in err for err in result.errors)

    def test_empty_base_sequence_list(self, simple_workflow):
        """Test that empty base_sequence is caught."""
        simple_workflow["base_sequence"] = []
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("at least one sequence step" in err for err in result.errors)

    def test_invalid_device_reference(self, workflow_missing_device_ref):
        """Test that invalid device reference is caught."""
        validator = WorkflowValidator()
        result = validator.validate(workflow_missing_device_ref)

        assert result.is_valid is False
        assert any("dev_missing" in err and "unknown device" in err for err in result.errors)

    def test_invalid_operation_reference_in_sequence(self, simple_workflow):
        """Test that invalid operation reference in sequence is caught."""
        simple_workflow["base_sequence"][0]["operation_id"] = "op_missing"
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("op_missing" in err and "unknown operation" in err for err in result.errors)

    def test_invalid_predecessor_reference(self, multi_device_workflow):
        """Test that invalid predecessor reference is caught."""
        multi_device_workflow["base_sequence"][1]["predecessors"] = ["op_missing"]
        validator = WorkflowValidator()
        result = validator.validate(multi_device_workflow)

        assert result.is_valid is False
        assert any("op_missing" in err and "not a valid operation" in err for err in result.errors)

    def test_circular_dependency_two_nodes(self, workflow_with_cycle):
        """Test that circular dependency A->B->A is caught."""
        validator = WorkflowValidator()
        result = validator.validate(workflow_with_cycle)

        assert result.is_valid is False
        assert any("circular" in err.lower() for err in result.errors)

    def test_circular_dependency_three_nodes(self, simple_workflow):
        """Test that circular dependency A->B->C->A is caught."""
        # Add two more operations
        simple_workflow["operations"].extend([
            {
                "operation_id": "op_b",
                "operation_name": "Op B",
                "device_id": "dev1",
                "timing": {"type": "fixed", "value": 10.0},
                "operation_type": "processing"
            },
            {
                "operation_id": "op_c",
                "operation_name": "Op C",
                "device_id": "dev1",
                "timing": {"type": "fixed", "value": 10.0},
                "operation_type": "processing"
            }
        ])

        # Create circular dependency: op1 -> op_b -> op_c -> op1
        simple_workflow["base_sequence"] = [
            {"sequence_id": 1, "operation_id": "op1", "predecessors": ["op_c"]},
            {"sequence_id": 2, "operation_id": "op_b", "predecessors": ["op1"]},
            {"sequence_id": 3, "operation_id": "op_c", "predecessors": ["op_b"]}
        ]

        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("circular" in err.lower() for err in result.errors)

    def test_self_reference_circular_dependency(self, simple_workflow):
        """Test that self-referencing predecessor is caught."""
        simple_workflow["base_sequence"][0]["predecessors"] = ["op1"]
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("circular" in err.lower() for err in result.errors)

    def test_timing_fixed_missing_value(self, simple_workflow):
        """Test that fixed timing without value is caught."""
        simple_workflow["operations"][0]["timing"] = {"type": "fixed"}
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("fixed timing requires 'value'" in err for err in result.errors)

    def test_timing_fixed_negative_value(self, simple_workflow):
        """Test that negative fixed timing value is caught."""
        simple_workflow["operations"][0]["timing"] = {"type": "fixed", "value": -5.0}
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("must be non-negative" in err for err in result.errors)

    def test_timing_triangular_missing_min(self, simple_workflow):
        """Test that triangular without min is caught."""
        simple_workflow["operations"][0]["timing"] = {
            "type": "triangular",
            "mode": 10.0,
            "max": 12.0
        }
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("missing parameters" in err and "min" in err for err in result.errors)

    def test_timing_triangular_invalid_parameters(self, workflow_invalid_timing):
        """Test that triangular with min > mode is caught."""
        validator = WorkflowValidator()
        result = validator.validate(workflow_invalid_timing)

        assert result.is_valid is False
        assert any("must satisfy min <= mode <= max" in err for err in result.errors)

    def test_timing_triangular_negative_parameters(self, simple_workflow):
        """Test that triangular with negative parameters is caught."""
        simple_workflow["operations"][0]["timing"] = {
            "type": "triangular",
            "min": -5.0,
            "mode": 0.0,
            "max": 5.0
        }
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("must be non-negative" in err for err in result.errors)

    def test_timing_exponential_missing_mean(self, simple_workflow):
        """Test that exponential without mean is caught."""
        simple_workflow["operations"][0]["timing"] = {"type": "exponential"}
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("exponential timing requires 'mean'" in err for err in result.errors)

    def test_timing_exponential_non_positive_mean(self, simple_workflow):
        """Test that exponential with non-positive mean is caught."""
        simple_workflow["operations"][0]["timing"] = {
            "type": "exponential",
            "mean": 0.0
        }
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("must be positive" in err for err in result.errors)

    def test_timing_unsupported_type(self, simple_workflow):
        """Test that unsupported timing type is caught."""
        simple_workflow["operations"][0]["timing"] = {
            "type": "normal",
            "mean": 10.0,
            "std": 2.0
        }
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("unsupported timing type" in err.lower() for err in result.errors)

    def test_resource_capacity_zero(self, simple_workflow):
        """Test that resource capacity of 0 is caught."""
        simple_workflow["devices"][0]["resource_capacity"] = 0
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("resource_capacity must be at least 1" in err for err in result.errors)

    def test_resource_capacity_negative(self, simple_workflow):
        """Test that negative resource capacity is caught."""
        simple_workflow["devices"][0]["resource_capacity"] = -1
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        assert any("resource_capacity must be at least 1" in err for err in result.errors)

    def test_resource_capacity_valid_values(self, simple_workflow):
        """Test that valid resource capacities pass."""
        # Test capacity = 1
        simple_workflow["devices"][0]["resource_capacity"] = 1
        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)
        assert result.is_valid is True

        # Test capacity > 1
        simple_workflow["devices"][0]["resource_capacity"] = 5
        result = validator.validate(simple_workflow)
        assert result.is_valid is True

    def test_multiple_errors_reported(self, simple_workflow):
        """Test that multiple schema validation errors are reported together."""
        # Create multiple schema errors (logical validation only runs after schema passes)
        simple_workflow["devices"] = []
        simple_workflow["operations"] = []
        simple_workflow["base_sequence"] = []

        validator = WorkflowValidator()
        result = validator.validate(simple_workflow)

        assert result.is_valid is False
        # Should report errors for empty devices, operations, and base_sequence
        assert len(result.errors) >= 2


class TestScenarioValidator:
    """Tests for ScenarioValidator."""

    def test_valid_simple_scenario(self, simple_scenario, simple_workflow):
        """Test that a valid simple scenario passes validation."""
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario, simple_workflow)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_valid_synchronized_scenario(self, synchronized_scenario, multi_device_workflow):
        """Test that a valid synchronized scenario passes validation."""
        validator = ScenarioValidator()
        result = validator.validate(synchronized_scenario, multi_device_workflow)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_scenario_id(self, simple_scenario):
        """Test that missing scenario_id is caught."""
        del simple_scenario["scenario_id"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("scenario_id" in err for err in result.errors)

    def test_missing_workflow_id(self, simple_scenario):
        """Test that missing workflow_id is caught."""
        del simple_scenario["workflow_id"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("workflow_id" in err for err in result.errors)

    def test_missing_sample_entry_pattern(self, simple_scenario):
        """Test that missing sample_entry_pattern is caught."""
        del simple_scenario["sample_entry_pattern"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("sample_entry_pattern" in err for err in result.errors)

    def test_missing_simulation_config(self, simple_scenario):
        """Test that missing simulation_config is caught."""
        del simple_scenario["simulation_config"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("simulation_config" in err for err in result.errors)

    def test_workflow_id_mismatch(self, simple_scenario, multi_device_workflow):
        """Test that workflow_id mismatch is caught."""
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario, multi_device_workflow)

        assert result.is_valid is False
        assert any("test_simple" in err and "multi_device" in err for err in result.errors)

    def test_missing_pattern_type(self, simple_scenario):
        """Test that missing pattern_type is caught."""
        del simple_scenario["sample_entry_pattern"]["pattern_type"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("pattern_type" in err for err in result.errors)

    def test_unsupported_pattern_type(self, simple_scenario):
        """Test that unsupported pattern type is caught."""
        simple_scenario["sample_entry_pattern"]["pattern_type"] = "staggered"
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("unsupported pattern_type" in err.lower() for err in result.errors)

    def test_missing_num_samples(self, simple_scenario):
        """Test that missing num_samples is caught."""
        del simple_scenario["sample_entry_pattern"]["num_samples"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("num_samples" in err for err in result.errors)

    def test_num_samples_zero(self, simple_scenario):
        """Test that num_samples = 0 is caught."""
        simple_scenario["sample_entry_pattern"]["num_samples"] = 0
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("num_samples" in err and "positive" in err for err in result.errors)

    def test_num_samples_negative(self, simple_scenario):
        """Test that negative num_samples is caught."""
        simple_scenario["sample_entry_pattern"]["num_samples"] = -5
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("num_samples" in err for err in result.errors)

    def test_single_pattern_requires_one_sample(self, simple_scenario):
        """Test that 'single' pattern requires exactly 1 sample."""
        simple_scenario["sample_entry_pattern"]["num_samples"] = 5
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("single" in err and "num_samples=1" in err for err in result.errors)

    def test_synchronized_pattern_multiple_samples(self, synchronized_scenario):
        """Test that 'synchronized' pattern allows multiple samples."""
        validator = ScenarioValidator()
        result = validator.validate(synchronized_scenario)

        assert result.is_valid is True

    def test_random_seed_not_integer(self, simple_scenario):
        """Test that non-integer random_seed is caught."""
        simple_scenario["simulation_config"]["random_seed"] = "not an int"
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("random_seed" in err and "integer" in err for err in result.errors)

    def test_max_simulation_time_zero(self, simple_scenario):
        """Test that max_simulation_time = 0 is caught."""
        simple_scenario["simulation_config"]["max_simulation_time"] = 0
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("max_simulation_time" in err and "positive" in err for err in result.errors)

    def test_max_simulation_time_negative(self, simple_scenario):
        """Test that negative max_simulation_time is caught."""
        simple_scenario["simulation_config"]["max_simulation_time"] = -100
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert any("max_simulation_time" in err for err in result.errors)

    def test_optional_random_seed(self, simple_scenario):
        """Test that random_seed is optional."""
        del simple_scenario["simulation_config"]["random_seed"]
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is True

    def test_optional_max_simulation_time(self, simple_scenario):
        """Test that max_simulation_time is optional."""
        # Remove max_simulation_time if it exists
        simple_scenario["simulation_config"].pop("max_simulation_time", None)
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is True

    def test_validation_without_workflow(self, simple_scenario):
        """Test that validation works without providing workflow."""
        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is True

    def test_multiple_scenario_errors_reported(self, simple_scenario):
        """Test that multiple validation errors are reported together."""
        del simple_scenario["scenario_id"]
        simple_scenario["sample_entry_pattern"]["num_samples"] = 0
        simple_scenario["simulation_config"]["max_simulation_time"] = -100

        validator = ScenarioValidator()
        result = validator.validate(simple_scenario)

        assert result.is_valid is False
        assert len(result.errors) >= 2
