# Instrument Workflow Simulator - Phase 1a

Discrete-event simulation engine for diagnostic and clinical chemistry instrument workflow timing analysis.

## Project Status: Week 2 Complete ✅

**Implementation:** Phase 1a - Weeks 1 & 2 (Core Classes + SimPy Integration)
**Test Coverage:** 96% (144 tests passing)
**Status:** Ready for Week 3 (API + Advanced Statistics)

## What's Been Built

### Core Modules

1. **models.py** - Data structures for simulation
   - `SimulationEvent` - Individual event records with validation
   - `SimulationSummary` - Summary statistics dataclass
   - `ValidationResult` - Validation result container
   - Supporting dataclasses for queue stats, operation stats, etc.

2. **timing.py** - Distribution sampling functions
   - `sample_fixed()` - Deterministic timing
   - `sample_triangular()` - Three-point estimate distribution
   - `sample_exponential()` - Stochastic process timing
   - `sample_timing()` - Dispatcher function
   - `set_random_seed()` - Reproducible simulations

3. **validators.py** - Input validation
   - `WorkflowValidator` - Validates workflow JSON (schema, DAG, references)
   - `ScenarioValidator` - Validates scenario configurations

4. **core.py** - SimPy simulation engine (NEW in Week 2!)
   - `SimulationEngine` - Discrete-event simulation orchestration
   - Resource management with SimPy
   - Sample process coroutines
   - Event logging during execution
   - Deterministic simulations with random seeds
   - Support for device contention and queuing

### Test Suite

- **23 tests** for data models
- **29 tests** for timing distributions
- **65 tests** for validators
- **27 tests** for simulation engine (NEW!)
- **Total: 144 tests** with 96% code coverage

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src/simulation --cov-report=term-missing
```

## Usage Examples

### Validating a Workflow

```python
from src.simulation.validators import WorkflowValidator

workflow = {
    "workflow_id": "test_workflow",
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

validator = WorkflowValidator()
result = validator.validate(workflow)

if result.is_valid:
    print("Workflow is valid!")
else:
    print("Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Sampling from Timing Distributions

```python
from src.simulation.timing import sample_timing, set_random_seed

# For reproducible results
set_random_seed(42)

# Fixed timing (deterministic)
fixed = sample_timing({"type": "fixed", "value": 10.0})
# Result: 10.0

# Triangular distribution (min, mode, max)
triangular = sample_timing({
    "type": "triangular",
    "min": 8.0,
    "mode": 10.0,
    "max": 12.0
})
# Result: value between 8.0 and 12.0

# Exponential distribution (for stochastic processes)
exponential = sample_timing({
    "type": "exponential",
    "mean": 100.0
})
# Result: positive value with mean ~100.0
```

### Creating Simulation Events

```python
from src.simulation.models import SimulationEvent

event = SimulationEvent(
    timestamp=10.5,
    event_type="START",
    sample_id="SAMPLE_001",
    operation_id="load_sample",
    device_id="liquid_handler",
    duration=5.0,
    wait_time=2.0,
    device_queue_length=1,
    notes="Sample started processing"
)
```

## Project Structure

```
instrument-workflow-sim/
├── src/
│   └── simulation/
│       ├── __init__.py
│       ├── models.py           # Data structures (23 tests)
│       ├── timing.py           # Distribution sampling (29 tests)
│       └── validators.py       # Input validation (65 tests)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── test_models.py
│   ├── test_timing.py
│   └── test_validators.py
├── examples/                   # Example workflow JSON files
├── api/                        # Flask API (Week 3)
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

## Validation Features

### WorkflowValidator Checks

- ✅ Schema compliance (required fields, correct types)
- ✅ Device references (all device_ids exist)
- ✅ Operation references (all operation_ids exist)
- ✅ DAG validity (no circular dependencies)
- ✅ Timing model validity (correct parameters)
- ✅ Resource capacity (≥ 1)

### ScenarioValidator Checks

- ✅ Schema compliance
- ✅ Workflow reference matching
- ✅ Sample entry pattern validation
- ✅ Simulation config validation

## Timing Distributions

### Fixed
Deterministic timing for known durations.
```json
{"type": "fixed", "value": 10.0}
```

### Triangular
Three-point estimate (optimistic, most likely, pessimistic).
```json
{"type": "triangular", "min": 8.0, "mode": 10.0, "max": 12.0}
```

### Exponential
Stochastic processes with high variability.
```json
{"type": "exponential", "mean": 100.0}
```

## Test Coverage Summary

| Module | Lines | Coverage |
|--------|-------|----------|
| models.py | 76 | 97% |
| timing.py | 45 | 100% |
| validators.py | 205 | 93% |
| core.py | 97 | 99% |
| **Total** | **423** | **96%** |

## Next Steps - Week 3

Implement Flask API and advanced statistics:

1. Create Flask REST API endpoints (POST /api/simulate)
2. Implement full statistics computation in _compute_summary()
   - Device utilization calculation
   - Queue statistics (max queue length, average wait time)
   - Operation statistics (mean, stdev, min, max, median)
   - Bottleneck identification
3. Add example workflow JSON files
4. Create API integration tests
5. Deploy to Railway (optional)

## Development Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=src/simulation --cov-report=html

# Run specific test
pytest tests/test_timing.py::TestSampleFixed -v

# Install in development mode
pip install -e .
```

## Documentation

- **PROJECT_CONTEXT.md** - Project overview and key decisions
- **Phase_1a_Implementation_Specification.md** - Technical specification
- **CODING_GUIDELINES.md** - Code standards and testing
- **API_REFERENCE.md** - API endpoints (Week 3)
- **EXAMPLE_WORKFLOWS.md** - Sample workflow definitions

## Contributing

Follow the coding standards in `CODING_GUIDELINES.md`:
- Use type hints on all functions
- Write docstrings for all public methods (Google style)
- Maintain >90% test coverage
- Follow PEP 8 naming conventions

## License

Internal use - Systems Engineering Team

## Contact

For questions or issues, refer to the project documentation or contact the systems engineering team.
