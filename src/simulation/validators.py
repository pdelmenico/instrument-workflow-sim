"""Validation for workflow definitions and scenario configurations."""
from typing import Dict, List, Set, Any
from src.simulation.models import ValidationResult


class WorkflowValidator:
    """Validates workflow JSON against schema and logical constraints.

    Performs comprehensive validation including:
    - Schema compliance (required fields, correct types)
    - Reference integrity (device_ids, operation_ids)
    - DAG validity (no circular dependencies)
    - Timing model validity (correct parameters)
    - Resource capacity constraints
    """

    def validate(self, workflow: Dict[str, Any]) -> ValidationResult:
        """Validate a workflow definition.

        Args:
            workflow: Workflow dictionary to validate

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Schema validation
        errors.extend(self._validate_schema(workflow))

        # Only proceed with logical validation if schema is valid
        if not errors:
            errors.extend(self._validate_device_references(workflow))
            errors.extend(self._validate_operation_references(workflow))
            errors.extend(self._validate_dag(workflow))
            errors.extend(self._validate_timing_models(workflow))
            errors.extend(self._validate_resource_capacity(workflow))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_schema(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate required fields and types."""
        errors = []

        # Required top-level fields
        required_fields = ["workflow_id", "devices", "operations", "base_sequence"]
        for field in required_fields:
            if field not in workflow:
                errors.append(f"Workflow missing required field '{field}'")

        if errors:
            return errors

        # Validate devices is a list
        if not isinstance(workflow["devices"], list):
            errors.append("'devices' must be a list")
        elif len(workflow["devices"]) == 0:
            errors.append("Workflow must have at least one device")
        else:
            # Validate each device
            for idx, device in enumerate(workflow["devices"]):
                if not isinstance(device, dict):
                    errors.append(f"Device at index {idx} must be a dictionary")
                    continue

                required_device_fields = ["device_id", "device_name", "resource_capacity", "scheduling_policy"]
                for field in required_device_fields:
                    if field not in device:
                        errors.append(f"Device at index {idx} missing required field '{field}'")

        # Validate operations is a list
        if not isinstance(workflow["operations"], list):
            errors.append("'operations' must be a list")
        elif len(workflow["operations"]) == 0:
            errors.append("Workflow must have at least one operation")
        else:
            # Validate each operation
            for idx, operation in enumerate(workflow["operations"]):
                if not isinstance(operation, dict):
                    errors.append(f"Operation at index {idx} must be a dictionary")
                    continue

                required_op_fields = ["operation_id", "operation_name", "device_id", "timing", "operation_type"]
                for field in required_op_fields:
                    if field not in operation:
                        errors.append(f"Operation at index {idx} missing required field '{field}'")

        # Validate base_sequence is a list
        if not isinstance(workflow["base_sequence"], list):
            errors.append("'base_sequence' must be a list")
        elif len(workflow["base_sequence"]) == 0:
            errors.append("Workflow must have at least one sequence step")
        else:
            # Validate each sequence step
            for idx, step in enumerate(workflow["base_sequence"]):
                if not isinstance(step, dict):
                    errors.append(f"Sequence step at index {idx} must be a dictionary")
                    continue

                required_seq_fields = ["sequence_id", "operation_id", "predecessors"]
                for field in required_seq_fields:
                    if field not in step:
                        errors.append(f"Sequence step at index {idx} missing required field '{field}'")

                if "predecessors" in step and not isinstance(step["predecessors"], list):
                    errors.append(f"Sequence step at index {idx}: 'predecessors' must be a list")

        return errors

    def _validate_device_references(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate all device_id references exist."""
        errors = []

        # Get all device IDs
        device_ids = {device["device_id"] for device in workflow["devices"]}

        # Check operations reference valid devices
        for operation in workflow["operations"]:
            device_id = operation.get("device_id")
            if device_id and device_id not in device_ids:
                errors.append(
                    f"Operation '{operation.get('operation_id')}' references "
                    f"unknown device '{device_id}'"
                )

        return errors

    def _validate_operation_references(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate all operation_id references exist."""
        errors = []

        # Get all operation IDs
        operation_ids = {op["operation_id"] for op in workflow["operations"]}

        # Check base_sequence references valid operations
        for step in workflow["base_sequence"]:
            op_id = step.get("operation_id")
            if op_id and op_id not in operation_ids:
                errors.append(
                    f"Sequence step {step.get('sequence_id')} references "
                    f"unknown operation '{op_id}'"
                )

            # Check predecessors reference valid operations
            predecessors = step.get("predecessors", [])
            for pred in predecessors:
                if pred not in operation_ids:
                    errors.append(
                        f"Sequence step {step.get('sequence_id')} has predecessor "
                        f"'{pred}' which is not a valid operation"
                    )

        return errors

    def _validate_dag(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate base_sequence forms a valid DAG (no circular dependencies)."""
        errors = []

        # Build predecessor map
        predecessors_map = {}
        for step in workflow["base_sequence"]:
            op_id = step.get("operation_id")
            preds = step.get("predecessors", [])
            predecessors_map[op_id] = preds

        # Check for circular dependencies using DFS
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            """Detect cycle using recursive DFS."""
            visited.add(node)
            rec_stack.add(node)

            # Visit all predecessors
            for pred in predecessors_map.get(node, []):
                if pred not in visited:
                    if has_cycle(pred, visited, rec_stack):
                        return True
                elif pred in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for op_id in predecessors_map:
            if op_id not in visited:
                rec_stack = set()
                if has_cycle(op_id, visited, rec_stack):
                    errors.append(
                        f"Circular dependency detected in base_sequence involving "
                        f"operation '{op_id}'"
                    )
                    break

        return errors

    def _validate_timing_models(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate timing model parameters."""
        errors = []

        for operation in workflow["operations"]:
            timing = operation.get("timing")
            if not timing:
                continue

            op_id = operation.get("operation_id")
            timing_type = timing.get("type")

            if timing_type == "fixed":
                if "value" not in timing:
                    errors.append(f"Operation '{op_id}': fixed timing requires 'value' parameter")
                elif timing["value"] < 0:
                    errors.append(f"Operation '{op_id}': fixed timing value must be non-negative")

            elif timing_type == "triangular":
                required = ["min", "mode", "max"]
                missing = [p for p in required if p not in timing]
                if missing:
                    errors.append(
                        f"Operation '{op_id}': triangular timing missing parameters {missing}"
                    )
                else:
                    min_val = timing["min"]
                    mode = timing["mode"]
                    max_val = timing["max"]

                    if min_val < 0 or mode < 0 or max_val < 0:
                        errors.append(
                            f"Operation '{op_id}': triangular parameters must be non-negative"
                        )
                    elif not (min_val <= mode <= max_val):
                        errors.append(
                            f"Operation '{op_id}': triangular parameters must satisfy "
                            f"min <= mode <= max, got min={min_val}, mode={mode}, max={max_val}"
                        )

            elif timing_type == "exponential":
                if "mean" not in timing:
                    errors.append(f"Operation '{op_id}': exponential timing requires 'mean' parameter")
                elif timing["mean"] <= 0:
                    errors.append(f"Operation '{op_id}': exponential mean must be positive")

            else:
                errors.append(
                    f"Operation '{op_id}': unsupported timing type '{timing_type}'. "
                    f"Supported types: fixed, triangular, exponential"
                )

        return errors

    def _validate_resource_capacity(self, workflow: Dict[str, Any]) -> List[str]:
        """Validate resource capacity constraints."""
        errors = []

        for device in workflow["devices"]:
            capacity = device.get("resource_capacity")
            device_id = device.get("device_id")

            if capacity is not None and capacity < 1:
                errors.append(
                    f"Device '{device_id}': resource_capacity must be at least 1, got {capacity}"
                )

        return errors


class ScenarioValidator:
    """Validates scenario configuration."""

    def validate(self, scenario: Dict[str, Any], workflow: Dict[str, Any] = None) -> ValidationResult:
        """Validate a scenario configuration.

        Args:
            scenario: Scenario dictionary to validate
            workflow: Optional workflow to validate against

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Schema validation
        errors.extend(self._validate_schema(scenario))

        # Workflow reference validation
        if workflow:
            errors.extend(self._validate_workflow_reference(scenario, workflow))

        # Sample entry pattern validation
        errors.extend(self._validate_sample_entry_pattern(scenario))

        # Simulation config validation
        errors.extend(self._validate_simulation_config(scenario))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def _validate_schema(self, scenario: Dict[str, Any]) -> List[str]:
        """Validate required fields and types."""
        errors = []

        required_fields = ["scenario_id", "workflow_id", "sample_entry_pattern", "simulation_config"]
        for field in required_fields:
            if field not in scenario:
                errors.append(f"Scenario missing required field '{field}'")

        return errors

    def _validate_workflow_reference(self, scenario: Dict[str, Any], workflow: Dict[str, Any]) -> List[str]:
        """Validate scenario references correct workflow."""
        errors = []

        scenario_workflow_id = scenario.get("workflow_id")
        workflow_id = workflow.get("workflow_id")

        if scenario_workflow_id != workflow_id:
            errors.append(
                f"Scenario references workflow '{scenario_workflow_id}' but "
                f"provided workflow has id '{workflow_id}'"
            )

        return errors

    def _validate_sample_entry_pattern(self, scenario: Dict[str, Any]) -> List[str]:
        """Validate sample entry pattern configuration."""
        errors = []

        pattern = scenario.get("sample_entry_pattern", {})

        if not isinstance(pattern, dict):
            errors.append("'sample_entry_pattern' must be a dictionary")
            return errors

        # Validate pattern type
        pattern_type = pattern.get("pattern_type")
        if not pattern_type:
            errors.append("'sample_entry_pattern' missing 'pattern_type'")
        elif pattern_type not in ["synchronized", "single"]:
            errors.append(
                f"Unsupported pattern_type '{pattern_type}'. "
                f"Phase 1a supports: synchronized, single"
            )

        # Validate num_samples
        num_samples = pattern.get("num_samples")
        if num_samples is None:
            errors.append("'sample_entry_pattern' missing 'num_samples'")
        elif not isinstance(num_samples, int) or num_samples < 1:
            errors.append(f"'num_samples' must be a positive integer, got {num_samples}")

        # Pattern-specific validation
        if pattern_type == "single" and num_samples and num_samples != 1:
            errors.append(f"'single' pattern requires num_samples=1, got {num_samples}")

        return errors

    def _validate_simulation_config(self, scenario: Dict[str, Any]) -> List[str]:
        """Validate simulation configuration."""
        errors = []

        config = scenario.get("simulation_config", {})

        if not isinstance(config, dict):
            errors.append("'simulation_config' must be a dictionary")
            return errors

        # Validate random_seed (optional)
        if "random_seed" in config:
            seed = config["random_seed"]
            if not isinstance(seed, int):
                errors.append(f"'random_seed' must be an integer, got {type(seed).__name__}")

        # Validate max_simulation_time (optional)
        if "max_simulation_time" in config:
            max_time = config["max_simulation_time"]
            if not isinstance(max_time, (int, float)) or max_time <= 0:
                errors.append(f"'max_simulation_time' must be positive, got {max_time}")

        return errors
