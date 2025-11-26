# Phase 1a Implementation Checklist

Use this checklist when starting a Claude Code session for Phase 1a implementation.

---

## Pre-Implementation Setup

- [ ] Review `PROJECT_CONTEXT.md` for project overview and key decisions
- [ ] Review `Phase_1a_Implementation_Specification.md` Section 1-4 (Architecture + Data Models)
- [ ] Review `CODING_GUIDELINES.md` for Python standards and project structure
- [ ] Verify all required dependencies are in `requirements.txt`
- [ ] Create local virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Week 1: Core Classes (Validators + Timing)

### Task 1.1: Setup Project Structure
- [ ] Create directory structure as defined in CODING_GUIDELINES.md
- [ ] Create `__init__.py` files in all package directories
- [ ] Create `conftest.py` with shared pytest fixtures

**Files to create:**
- `src/simulation/__init__.py`
- `src/simulation/models.py`
- `src/simulation/validators.py`
- `src/simulation/timing.py`
- `api/__init__.py`
- `tests/__init__.py`
- `tests/conftest.py`

### Task 1.2: Implement Data Models (models.py)
- [ ] Create `SimulationEvent` dataclass with all fields from Phase_1a spec Section 3.3
- [ ] Create `SimulationSummary` dataclass with all fields from spec Section 3.4
- [ ] Add validation in `__post_init__` methods (e.g., timestamp >= 0)
- [ ] Write unit tests in `tests/test_models.py`

**Expected output:** 2 validated dataclasses, 8+ unit tests

### Task 1.3: Implement Timing Distribution Sampling (timing.py)
- [ ] Create `sample_fixed(value)` function
- [ ] Create `sample_triangular(min, mode, max)` function
- [ ] Create `sample_exponential(mean)` function
- [ ] Add input validation (e.g., min ≤ mode ≤ max for triangular)
- [ ] Write unit tests: verify distributions produce values in expected ranges

**Expected output:** 3 timing functions, deterministic with seed, 12+ unit tests

### Task 1.4: Implement WorkflowValidator (validators.py Part 1)
- [ ] Create `ValidationResult` dataclass (is_valid, errors[], warnings[])
- [ ] Create `WorkflowValidator` class with `validate()` method
- [ ] Implement JSON schema validation using jsonschema library
- [ ] Implement device reference validation (all device_ids in operations exist)
- [ ] Implement operation reference validation (all operation_ids in base_sequence exist)
- [ ] Implement DAG validation (no circular predecessor chains)
- [ ] Implement timing model validation (correct parameters for each type)
- [ ] Write comprehensive unit tests

**Expected output:** WorkflowValidator class, 20+ unit tests, clear error messages

**Test cases:**
- ✅ Valid workflow passes
- ❌ Missing 'devices' field
- ❌ Missing 'operations' field
- ❌ Invalid device_id reference
- ❌ Invalid operation_id reference
- ❌ Circular predecessor: A→B→A
- ❌ Circular predecessor: A→B→C→A
- ❌ Invalid timing: triangular with min > max
- ❌ Invalid timing: exponential with negative mean

### Task 1.5: Implement ScenarioValidator (validators.py Part 2)
- [ ] Create `ScenarioValidator` class with `validate()` method
- [ ] Validate scenario references correct workflow_id
- [ ] Validate sample_entry_pattern is known type (synchronized, single)
- [ ] Validate num_samples >= 1
- [ ] Validate simulation_config has valid random_seed and max_simulation_time
- [ ] Write unit tests

**Expected output:** ScenarioValidator class, 8+ unit tests

**Test cases:**
- ✅ Valid scenario (single pattern)
- ✅ Valid scenario (synchronized pattern)
- ❌ Unknown pattern_type
- ❌ num_samples = 0
- ❌ negative max_simulation_time
- ❌ workflow_id doesn't exist (or handle gracefully)

### Week 1 Deliverable
- ✅ models.py: SimulationEvent, SimulationSummary (tested)
- ✅ timing.py: fixed, triangular, exponential (tested, deterministic with seed)
- ✅ validators.py: WorkflowValidator, ScenarioValidator (tested)
- ✅ Test suite: >40 unit tests, >90% coverage on these modules
- ✅ All tests passing locally

**Quick Validation:**
```bash
pytest tests/ -v --cov=src/simulation
# Should see: PASSED for >40 tests, coverage >90%
```

---

## Week 2: SimPy Integration (Core Engine)

### Task 2.1: Implement SimulationEngine Initialization
- [ ] Create `SimulationEngine` class with `__init__(workflow, scenario)`
- [ ] Store workflow, scenario, initialize SimPy environment
- [ ] Create `initialize_resources()` method to build SimPy Resource per device
- [ ] Create `_compute_entry_times()` method for synchronized/single patterns
- [ ] Write unit tests for initialization

**Expected output:** SimulationEngine initialized correctly, resources created

### Task 2.2: Implement Sample Process Coroutine
- [ ] Create `_sample_process(sample_id, entry_time)` generator method
- [ ] Implement linear sequence execution (each op has ≤1 predecessor)
- [ ] For each operation:
  - Wait for entry time (if first operation)
  - Find operation definition
  - Acquire device resource (with queue tracking)
  - Record QUEUED event
  - Sample timing from distribution
  - Record START event
  - Yield timeout for operation duration
  - Record COMPLETE event
  - Release device resource
- [ ] Write integration tests with simple workflows

**Expected output:** _sample_process coroutine working, events logged correctly

### Task 2.3: Implement _sample_timing Method
- [ ] Create `_sample_timing(timing_model)` method
- [ ] Dispatch to timing.py functions based on timing_model['type']
- [ ] Handle all three distributions: fixed, triangular, exponential
- [ ] Raise clear error on unsupported timing types
- [ ] Write unit tests

**Expected output:** _sample_timing routing correctly to timing functions

### Task 2.4: Implement Event Logging
- [ ] Create `EventLogger` class (or integrate into SimulationEngine)
- [ ] Implement `record(event: SimulationEvent)` method
- [ ] Implement `to_dataframe()` method for Pandas analysis
- [ ] Implement `export_json()` method
- [ ] Write unit tests

**Expected output:** EventLogger working, events exported correctly

### Task 2.5: Implement run() Method
- [ ] Create `run()` method that orchestrates entire simulation
- [ ] Initialize resources
- [ ] Compute entry times
- [ ] Start sample processes for each sample
- [ ] Run SimPy environment
- [ ] Call `_compute_summary()` (stub for now)
- [ ] Return event_log, summary
- [ ] Write integration tests

**Expected output:** run() completes without errors, returns event_log + summary

### Task 2.6: Write Integration Tests
- [ ] Test: Single sample, single device, fixed timing (deterministic output)
- [ ] Test: Single sample, two devices sequential
- [ ] Test: Synchronized batch (2 samples), device contention
- [ ] Test: Reproducibility with same random_seed
- [ ] Test: Queue delays visible in event log for contended device

**Expected output:** 5+ integration tests passing

### Week 2 Deliverable
- ✅ SimulationEngine class fully functional
- ✅ _sample_process coroutine working for linear sequences
- ✅ Event logging capturing all state changes
- ✅ Integration tests: single sample, synchronized batch, deterministic with seed
- ✅ All tests passing locally

**Quick Validation:**
```bash
pytest tests/test_simulation_engine.py -v
# Should see: PASSED for >15 tests
```

---

## Week 3: Statistics & API

### Task 3.1: Implement _compute_summary() Method
- [ ] Group events by device, operation, sample
- [ ] Calculate device utilization = (device busy time) / (total simulation time)
- [ ] Calculate device queue stats: max queue length, avg queue time
- [ ] Calculate operation stats: mean/stdev/min/max duration per operation
- [ ] Calculate operation wait times: mean wait, total wait per operation
- [ ] Calculate total throughput = samples_completed / total_simulation_time
- [ ] Calculate mean sample cycle time = total_simulation_time / samples_completed
- [ ] Identify bottleneck device (highest utilization)
- [ ] Return SimulationSummary dataclass
- [ ] Write unit tests

**Expected output:** _compute_summary() produces accurate statistics

### Task 3.2: Implement Flask API Infrastructure
- [ ] Create `main.py` Flask app initialization
- [ ] Create `api/routes.py` with endpoint stubs
- [ ] Implement request/response validation using marshmallow or pydantic
- [ ] Implement error handling middleware
- [ ] Add logging configuration
- [ ] Write unit tests for Flask app setup

**Expected output:** Flask app runs, basic error handling working

### Task 3.3: Implement POST /api/simulate Endpoint
- [ ] Parse request JSON (workflow + scenario)
- [ ] Validate both using WorkflowValidator and ScenarioValidator
- [ ] If validation fails, return 400 with error details
- [ ] If validation succeeds, instantiate SimulationEngine
- [ ] Call engine.run()
- [ ] Store run results (run_id → events + summary)
- [ ] Return response with run_id + summary
- [ ] Write integration tests

**Expected output:** POST endpoint working, returns proper response format

### Task 3.4: Implement GET /api/simulation/{run_id}/events Endpoint
- [ ] Retrieve event log for run_id
- [ ] Support optional filtering (sample_id, operation_id, device_id, event_type)
- [ ] Support pagination (limit, offset)
- [ ] Return events as JSON array
- [ ] Write integration tests

**Expected output:** GET events endpoint working with filtering

### Task 3.5: Implement GET /api/simulation/{run_id}/summary Endpoint
- [ ] Retrieve summary for run_id
- [ ] Return summary object as JSON
- [ ] Write integration tests

**Expected output:** GET summary endpoint working

### Task 3.6: Implement Data Persistence (SQLite)
- [ ] Create database schema for storing runs, events, summaries
- [ ] Implement save_run(run_id, events, summary) method
- [ ] Implement load_run(run_id) method
- [ ] Implement cleanup (optional: delete old runs)
- [ ] Write integration tests

**Expected output:** Runs persisted to SQLite, retrievable

### Task 3.7: Write End-to-End API Tests
- [ ] Test: POST /api/simulate with Example 1 workflow, get summary back
- [ ] Test: GET /api/simulation/{run_id}/events returns all events
- [ ] Test: GET /api/simulation/{run_id}/summary returns correct statistics
- [ ] Test: Validation error returns 400 with clear message
- [ ] Test: Missing run_id returns 404
- [ ] Test: Filtering by sample_id works
- [ ] Test: Deterministic results with same seed

**Expected output:** 7+ end-to-end tests passing

### Task 3.8: Performance Optimization & Documentation
- [ ] Profile simulation with 100-sample, 20-operation workflow
- [ ] Verify <2 sec execution time (or log issues)
- [ ] Update docstrings and code comments
- [ ] Generate API documentation
- [ ] Create example request/response JSON files
- [ ] Write README.md with setup instructions

**Expected output:** Performance documented, clear setup/usage docs

### Week 3 Deliverable
- ✅ SimulationEngine._compute_summary() accurate
- ✅ Flask API with 3 endpoints (POST /simulate, GET /events, GET /summary)
- ✅ SQLite persistence working
- ✅ End-to-end integration tests: 7+
- ✅ Performance benchmarked: 100-sample workflow <2 sec
- ✅ Documentation complete (API reference, setup, examples)

**Final Validation:**
```bash
pytest tests/ -v --cov=src
# Should see: PASSED for >70 tests, coverage >90%

# Manual test
python main.py &
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d @examples/single_sample_pcr.json
# Should get: 200 OK with run_id and summary
```

---

## Testing Strategy

### Unit Tests (Week 1-2)
- **models.py:** Data validation, edge cases
- **timing.py:** Distribution sampling, bounds checking, determinism
- **validators.py:** Schema compliance, logical validation, error messages
- **SimulationEngine (core):** Initialization, resource creation, entry times

### Integration Tests (Week 2-3)
- **SimulationEngine (end-to-end):** Single sample, sync batch, contention
- **Statistics:** Accuracy of utilization, throughput, bottleneck detection
- **API endpoints:** Request validation, response format, error handling
- **Determinism:** Same seed produces identical results

### Test Execution
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_validators.py -v

# Run specific test
pytest tests/test_simulation_engine.py::test_single_sample_fixed_timing -v

# Run with logging output
pytest tests/ -v -s

# Run performance test
pytest tests/test_performance.py -v --durations=10
```

---

## Common Issues & Troubleshooting

### Issue: "Module 'simpy' not found"
- **Solution:** `pip install -r requirements.txt` and verify venv activated

### Issue: "Circular dependency not detected"
- **Solution:** Verify DAG validation uses topological sort and catches cycles

### Issue: "Random seed not producing deterministic results"
- **Solution:** Set NumPy seed: `np.random.seed(seed)` in addition to SimPy seed

### Issue: "Events out of timestamp order"
- **Solution:** SimPy processes events in order; if not, check event_log append logic

### Issue: "API returns 500 error"
- **Solution:** Check Flask logs, add try/catch with logging in endpoint

### Issue: "Database file growing too large"
- **Solution:** Implement cleanup or compress event logs in Phase 1b

---

## Acceptance Criteria Checklist

Phase 1a is complete when:

- [ ] ✅ WorkflowValidator rejects circular dependencies, missing refs, invalid timing
- [ ] ✅ ScenarioValidator accepts synchronized/single, rejects invalid configs
- [ ] ✅ SimulationEngine produces event logs with correct timestamps, device contention, queue wait times
- [ ] ✅ Statistics accurately identify bottleneck device and queue delays
- [ ] ✅ Flask API accepts JSON, returns event log + summary in <1 sec for 10-sample batch
- [ ] ✅ All timing distributions (fixed, triangular, exponential) sample correctly, deterministically with seed
- [ ] ✅ Test suite covers single/multi-device, sync batch, validation failures (70+ tests, >90% coverage)
- [ ] ✅ Documentation complete: API reference, setup guide, examples, coding standards
- [ ] ✅ Code follows CODING_GUIDELINES.md standards
- [ ] ✅ All tests pass: `pytest tests/ -v` shows 0 failures

---

## Session Context Checkpoints

**Before starting Week 1:**
- [ ] All documents reviewed (PROJECT_CONTEXT, Phase_1a_spec, CODING_GUIDELINES)
- [ ] Project structure created
- [ ] Virtual environment set up
- [ ] Dependencies installed

**Before starting Week 2:**
- [ ] Week 1 deliverables complete
- [ ] All Week 1 tests passing (>40, >90% coverage)
- [ ] Code review completed or self-reviewed against CODING_GUIDELINES

**Before starting Week 3:**
- [ ] Week 2 deliverables complete
- [ ] All Week 2 tests passing (>15 integration tests)
- [ ] SimPy basics understood (environments, resources, processes, events)

**At end of Week 3:**
- [ ] All tests passing: `pytest tests/ -v` shows PASSED for 70+ tests
- [ ] Coverage >90%: `pytest --cov=src --cov-report=term-missing`
- [ ] Performance acceptable: 100-sample workflow <2 sec
- [ ] Code review completed
- [ ] Documentation generated
- [ ] Ready for Phase 1b kickoff

---

## Quick Reference: Key Files

| File | Purpose | Week |
|------|---------|------|
| `src/simulation/models.py` | SimulationEvent, SimulationSummary dataclasses | W1 |
| `src/simulation/timing.py` | Distribution sampling functions | W1 |
| `src/simulation/validators.py` | WorkflowValidator, ScenarioValidator | W1 |
| `src/simulation/core.py` | SimulationEngine class | W2 |
| `api/routes.py` | Flask endpoints | W3 |
| `tests/conftest.py` | Pytest fixtures | W1 |
| `tests/test_*.py` | Unit and integration tests | W1-W3 |
| `main.py` | Flask app entry point | W3 |
| `requirements.txt` | Python dependencies | Setup |
| `examples/*.json` | Example workflows for testing | Setup |

