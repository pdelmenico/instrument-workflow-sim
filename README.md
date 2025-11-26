# Instrument Workflow Simulator - Phase 1a

Discrete-event simulation engine for diagnostic and clinical chemistry instrument workflow timing analysis.

## Project Status: Week 3 Complete ✅ - Phase 1a DONE

**Implementation:** Phase 1a Complete - All 3 Weeks (Core Classes + SimPy + Flask API)
**Test Coverage:** 94% (165 tests passing)
**Status:** Production-ready simulation engine with REST API

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

4. **core.py** - SimPy simulation engine
   - `SimulationEngine` - Discrete-event simulation orchestration
   - Resource management with SimPy
   - Sample process coroutines
   - Event logging during execution
   - Deterministic simulations with random seeds
   - Support for device contention and queuing
   - Full statistics computation (device utilization, queue stats, bottleneck identification)

### Flask REST API (NEW in Week 3!)

5. **main.py** - Flask application entry point
   - Application factory pattern
   - CORS support for web accessibility
   - Blueprint registration

6. **api/routes.py** - REST API endpoints
   - `POST /api/simulate` - Execute simulation with workflow and scenario
   - `GET /api/simulation/{run_id}/events` - Retrieve event log with filters
   - `GET /api/simulation/{run_id}/summary` - Get summary statistics
   - `GET /api/health` - Health check endpoint
   - In-memory result storage (production would use database)

### Example Workflows

7. **examples/single_sample_pcr.json** - Single-sample PCR workflow
8. **examples/synchronized_batch_analyzer.json** - 3-sample batch chemistry analyzer

### Test Suite

- **23 tests** for data models
- **29 tests** for timing distributions
- **65 tests** for validators
- **27 tests** for simulation engine
- **21 tests** for Flask API (NEW!)
- **Total: 165 tests** with 94% code coverage

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
pytest tests/ -v --cov=src/simulation --cov=api --cov-report=term-missing

# Run Flask API server
python main.py
# Server will start on http://0.0.0.0:5000
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

### Using the REST API

```bash
# Start the Flask server
python main.py

# In another terminal, run a simulation using curl
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d @examples/single_sample_pcr.json

# Response will include run_id, execution time, and summary statistics

# Get event log for a specific run
curl http://localhost:5000/api/simulation/{run_id}/events

# Get summary statistics
curl http://localhost:5000/api/simulation/{run_id}/summary

# Filter events by sample
curl "http://localhost:5000/api/simulation/{run_id}/events?sample_id=SAMPLE_000"

# Filter events by event type
curl "http://localhost:5000/api/simulation/{run_id}/events?event_type=START"

# Paginate events
curl "http://localhost:5000/api/simulation/{run_id}/events?limit=10&offset=0"

# Health check
curl http://localhost:5000/api/health
```

### Running a Simulation Programmatically

```python
from src.simulation.core import SimulationEngine
from src.simulation.validators import WorkflowValidator, ScenarioValidator
import json

# Load workflow and scenario
with open('examples/single_sample_pcr.json') as f:
    data = json.load(f)
    workflow = data['workflow']
    scenario = data['scenario']

# Validate inputs
workflow_validator = WorkflowValidator()
workflow_result = workflow_validator.validate(workflow)

scenario_validator = ScenarioValidator()
scenario_result = scenario_validator.validate(scenario, workflow)

if workflow_result.is_valid and scenario_result.is_valid:
    # Run simulation
    engine = SimulationEngine(workflow, scenario)
    events, summary = engine.run()

    print(f"Simulation completed in {summary.total_simulation_time:.2f}s")
    print(f"Samples completed: {summary.num_samples_completed}")
    print(f"Throughput: {summary.total_throughput:.6f} samples/sec")
    print(f"Bottleneck device: {summary.bottleneck_device}")
    print(f"Bottleneck utilization: {summary.bottleneck_utilization:.1%}")
```

## Project Structure

```
instrument-workflow-sim/
├── src/
│   └── simulation/
│       ├── __init__.py
│       ├── models.py           # Data structures (23 tests)
│       ├── timing.py           # Distribution sampling (29 tests)
│       ├── validators.py       # Input validation (65 tests)
│       └── core.py             # SimPy simulation engine (27 tests)
├── api/
│   ├── __init__.py
│   └── routes.py               # Flask REST API routes (21 tests)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── test_models.py
│   ├── test_timing.py
│   ├── test_validators.py
│   ├── test_simulation_engine.py
│   └── test_api.py
├── examples/
│   ├── single_sample_pcr.json
│   └── synchronized_batch_analyzer.json
├── main.py                     # Flask application entry point
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
| core.py | 136 | 97% |
| routes.py | 97 | 89% |
| **Total** | **559** | **94%** |

## Phase 1a Deliverables ✅

All Phase 1a objectives completed:

1. ✅ **Core Data Structures** - Dataclasses for events, summaries, and validation
2. ✅ **Timing Distributions** - Fixed, triangular, and exponential sampling
3. ✅ **Input Validation** - Schema validation, DAG cycle detection, reference integrity
4. ✅ **SimPy Integration** - Discrete-event simulation with resource contention
5. ✅ **Event Logging** - Comprehensive event tracking (QUEUED, START, COMPLETE)
6. ✅ **Statistics Computation** - Device utilization, queue stats, bottleneck identification
7. ✅ **Flask REST API** - Four endpoints for simulation execution and results retrieval
8. ✅ **Example Workflows** - PCR and chemistry analyzer workflows
9. ✅ **Comprehensive Testing** - 165 tests with 94% coverage

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/simulate` | Execute simulation with workflow and scenario |
| GET | `/api/simulation/{run_id}/events` | Retrieve event log (supports filters and pagination) |
| GET | `/api/simulation/{run_id}/summary` | Get summary statistics for a completed simulation |
| GET | `/api/health` | Health check endpoint |

## Statistics Computed

- **Device Utilization**: Fraction of time each device was busy (0-1 range, accounts for multi-capacity)
- **Queue Statistics**: Max queue length, average wait time, total queue time per device
- **Operation Statistics**: Mean, stdev, min, max, median duration, sample count per operation
- **Bottleneck Identification**: Device with highest utilization and associated queue delay
- **Cycle Time Metrics**: Mean, min, max sample cycle time
- **Throughput**: Samples completed per unit time

## Next Phase - Phase 1b (Future)

Potential enhancements for Phase 1b:

1. Stochastic entry patterns (Poisson arrivals, scheduled batches)
2. Advanced scheduling policies (Priority, SJF, Resource optimization)
3. Parallel operation support (DAG execution)
4. Sample failure modeling and error scenarios
5. Database persistence (PostgreSQL)
6. Real-time simulation monitoring
7. Visualization dashboard

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
