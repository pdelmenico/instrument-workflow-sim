# Phase 1a Development Guidelines

## Project Structure

```
instrument-workflow-sim/
├── src/
│   └── simulation/
│       ├── __init__.py
│       ├── core.py                 # SimulationEngine, EventLogger
│       ├── validators.py           # WorkflowValidator, ScenarioValidator
│       ├── models.py               # Dataclasses: SimulationEvent, SimulationSummary
│       └── timing.py               # Timing distribution sampling
├── api/
│   ├── __init__.py
│   └── routes.py                   # Flask endpoints
├── tests/
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_simulation_engine.py
│   ├── test_api_endpoints.py
│   └── fixtures/
│       └── example_workflows.py    # Reusable test workflows
├── examples/
│   ├── single_sample_pcr.json
│   ├── synchronized_batch_analyzer.json
│   └── multi_device_workflow.json
├── requirements.txt
├── setup.py
├── README.md
└── main.py                         # Flask app entry point
```

## Code Style & Standards

### Python Version
- Target: Python 3.9+
- Use type hints throughout (PEP 484)
- Use dataclasses (Python 3.7+) for data models

### Naming Conventions
- Class names: PascalCase (WorkflowValidator, SimulationEngine)
- Function/method names: snake_case (validate_workflow, sample_timing)
- Constants: UPPER_SNAKE_CASE (MAX_SIMULATION_TIME)
- Private methods: _leading_underscore (_sample_process, _compute_summary)

### Code Organization
- One class per major responsibility
- Methods <40 lines (refactor complex logic to helper methods)
- Clear docstrings on all public methods
- Use type hints on all function signatures

Example:

```python
from typing import Dict, List, Tuple
from dataclasses import dataclass
import simpy

@dataclass
class SimulationEvent:
    """Represents a single event in the simulation timeline."""
    timestamp: float
    event_type: str  # "QUEUED", "START", "COMPLETE", "RELEASED"
    sample_id: str
    operation_id: str
    device_id: str
    duration: float
    wait_time: float
    device_queue_length: int
    notes: str = ""

class SimulationEngine:
    """Orchestrates discrete-event simulation using SimPy."""
    
    def __init__(self, workflow: Dict, scenario: Dict) -> None:
        """
        Initialize simulation engine.
        
        Args:
            workflow: Validated workflow JSON definition
            scenario: Validated scenario configuration
        
        Raises:
            ValueError: If workflow or scenario is invalid
        """
        self.workflow = workflow
        self.scenario = scenario
        self.env = simpy.Environment()
        self.event_log: List[SimulationEvent] = []
        self.resources: Dict[str, simpy.Resource] = {}
```

### Import Organization
```python
# Standard library
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Third-party
import simpy
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import jsonschema

# Local
from simulation.models import SimulationEvent, SimulationSummary
from simulation.validators import WorkflowValidator
```

### Error Handling

Use custom exceptions for domain-specific errors:

```python
class WorkflowError(Exception):
    """Base exception for workflow-related errors."""
    pass

class ValidationError(WorkflowError):
    """Raised when workflow or scenario validation fails."""
    pass

class InvalidTimingModelError(WorkflowError):
    """Raised when timing model parameters are invalid."""
    pass

class SimulationError(WorkflowError):
    """Raised during simulation execution."""
    pass

# Usage
def validate_workflow(workflow: Dict) -> None:
    if 'devices' not in workflow:
        raise ValidationError("Workflow must define 'devices' list")
    
    if not isinstance(workflow['devices'], list):
        raise ValidationError("'devices' must be a list")
    
    if len(workflow['devices']) == 0:
        raise ValidationError("Workflow must have at least one device")
```

### Logging

Use Python's logging module consistently:

```python
import logging

logger = logging.getLogger(__name__)

class SimulationEngine:
    def run(self) -> Tuple[List[SimulationEvent], SimulationSummary]:
        logger.info(f"Starting simulation for workflow '{self.workflow['workflow_id']}'")
        
        try:
            self.initialize_resources()
            entry_times = self._compute_entry_times()
            
            logger.debug(f"Generated {len(entry_times)} sample entry times")
            
            for sample_id, entry_time in entry_times:
                self.env.process(self._sample_process(sample_id, entry_time))
            
            self.env.run(until=max_time)
            logger.info(f"Simulation completed. Processed {len(self.event_log)} events")
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}", exc_info=True)
            raise SimulationError(f"Simulation execution failed: {str(e)}")
        
        return self.event_log, self._compute_summary()
```

## Testing Standards

### Test File Organization
- One test file per module (test_validators.py, test_simulation_engine.py)
- Use pytest framework
- Fixtures in conftest.py or within test files

### Test Naming
- Test functions: `test_<description>_<expected_outcome>`
- Fixtures: `<object_name>_fixture`

Examples:
```python
def test_validator_rejects_missing_devices():
    """WorkflowValidator should reject workflows without devices list."""
    pass

def test_simulation_engine_single_sample_fixed_timing():
    """SimulationEngine should complete single-sample workflow with fixed timing."""
    pass

def test_circular_dependency_detected():
    """Validator should detect circular predecessor chains."""
    pass
```

### Fixture Design
```python
# conftest.py or test_fixtures.py
import pytest

@pytest.fixture
def simple_workflow():
    """Minimal valid workflow with one device, one operation."""
    return {
        "workflow_id": "test_simple",
        "workflow_name": "Simple Test Workflow",
        "devices": [{
            "device_id": "dev1",
            "device_name": "Test Device",
            "resource_capacity": 1,
            "scheduling_policy": "FIFO"
        }],
        "operations": [{
            "operation_id": "op1",
            "operation_name": "Test Operation",
            "device_id": "dev1",
            "timing": {"type": "fixed", "value": 10.0},
            "operation_type": "processing"
        }],
        "base_sequence": [{
            "sequence_id": 1,
            "operation_id": "op1",
            "predecessors": []
        }]
    }

@pytest.fixture
def simple_scenario():
    """Minimal valid scenario."""
    return {
        "scenario_id": "test_scenario",
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
```

### Test Coverage
- Aim for >90% code coverage
- Use coverage.py: `pytest --cov=src tests/`
- All public methods must have at least one test
- All error paths must be tested

## Documentation Standards

### Docstring Format (Google style)
```python
def sample_timing(self, timing_model: Dict[str, float]) -> float:
    """
    Sample operation duration from timing model.
    
    Supports fixed, triangular, and exponential distributions.
    Uses NumPy's random number generator for consistency.
    
    Args:
        timing_model: Dict with 'type' and distribution parameters.
            Examples:
            - {"type": "fixed", "value": 10.0}
            - {"type": "triangular", "min": 5, "mode": 10, "max": 15}
            - {"type": "exponential", "mean": 30.0}
    
    Returns:
        Sampled duration in seconds (float).
    
    Raises:
        ValueError: If timing_model has invalid type or parameters.
    
    Example:
        >>> timing_model = {"type": "fixed", "value": 10.0}
        >>> duration = engine.sample_timing(timing_model)
        >>> assert duration == 10.0
    """
    pass
```

### Comment Guidelines
- Use comments for WHY, not WHAT (code shows what it does)
- Keep comments concise (one line preferred)
- Update comments when code changes

```python
# Good: explains non-obvious logic
# Using mode for triangular instead of mean because engineers estimate
# the "most likely" duration rather than mathematical expectation
return np.random.triangular(min_val, mode_val, max_val)

# Bad: redundant, explains what code obviously does
# Increment counter
counter += 1
```

## Performance Considerations

### Key Optimization Areas
1. **Event log growth** - For large simulations, event_log list can become huge
   - Mitigation: Consider streaming events to disk in Phase 1c if needed
   
2. **Resource lookup** - Repeated lookups of device_id → resource mapping
   - Mitigation: Pre-compute dict at initialization (already done in code)
   
3. **Statistics computation** - Full pass over event log to compute summaries
   - Mitigation: Acceptable for Phase 1a; optimize in Phase 1b if needed

4. **Random number generation** - NumPy's random functions are fast; use numpy.random module consistently

### Profiling
Use cProfile for performance profiling:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
engine = SimulationEngine(workflow, scenario)
events, summary = engine.run()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

## Version Control

### Commit Messages
- Use present tense: "Add validator" not "Added validator"
- Be specific: "Add circular dependency detection to WorkflowValidator" not "Fix bug"
- Reference issues if applicable: "Fix #42: Handle empty sequence"

### Branch Strategy
- Main branch: stable, production-ready code
- Feature branches: `feature/validator-implementation`
- Bug fixes: `bugfix/circular-dependency-detection`
- Docs: `docs/update-api-documentation`

## Configuration Management

### Environment Variables
```python
# config.py
import os

class Config:
    """Base configuration."""
    MAX_SIMULATION_TIME = int(os.getenv('MAX_SIMULATION_TIME', 86400))
    RANDOM_SEED = int(os.getenv('RANDOM_SEED', 42))
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
```

### Usage
```python
from config import DevelopmentConfig as Config

app = Flask(__name__)
app.config.from_object(Config)
```

## Dependency Management

### requirements.txt
```
simpy>=4.0.1
numpy>=1.21.0
pandas>=1.3.0
flask>=2.0.0
jsonschema>=4.0
pytest>=7.0
pytest-cov>=3.0
```

### Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Continuous Integration (Phase 1c)

Placeholder for CI/CD setup:
- Run tests on every commit
- Check code coverage >90%
- Lint with flake8 or pylint
- Type checking with mypy

## Debugging Tips

### Using pdb (Python debugger)
```python
import pdb

def _sample_process(self, sample_id: str, entry_time: float):
    yield self.env.timeout(entry_time)
    
    # Breakpoint
    pdb.set_trace()
    
    for step in self.workflow['base_sequence']:
        # Debug code
        pass
```

### Logging During Development
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Event log has {len(self.event_log)} events")
logger.debug(f"Devices: {list(self.resources.keys())}")
```

### Print Debugging (Last Resort)
```python
print(f"DEBUG: sample_id={sample_id}, device_id={device_id}, wait_time={wait_time}")
```

## Code Review Checklist

Before submitting code for review:

- ✅ All functions have type hints
- ✅ All public methods have docstrings
- ✅ Code follows naming conventions
- ✅ No commented-out code blocks
- ✅ Test coverage >90% for new code
- ✅ All tests pass locally
- ✅ No hardcoded values (use constants)
- ✅ Error messages are clear and actionable
- ✅ Logging is appropriate (not too verbose)
- ✅ No unused imports or variables

