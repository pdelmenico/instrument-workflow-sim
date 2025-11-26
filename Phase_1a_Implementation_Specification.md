# Phase 1a Implementation Specification
## Discrete-Event Simulation Engine - Core

**Version:** 1.0  
**Status:** Draft - Ready for team review  
**Scope:** Workflow validation, event logging, timing sampling, SimPy integration  
**Target Delivery:** Single-sample and synchronized batch simulation with fixed/triangular/exponential timing

---

## 1. Overview

Phase 1a delivers a working simulation engine that accepts workflow definitions (JSON) and scenario configurations, executes discrete-event simulation using SimPy, generates detailed event logs, and produces summary statistics for bottleneck identification.

**Success Criteria:**
- Load workflow JSON without manual editing
- Simulate single sample workflow with deterministic output
- Simulate synchronized batch (N samples entering simultaneously)
- Generate event timeline showing device contention and queue wait times
- Produce summary statistics: device utilization, operation durations, bottleneck identification
- All events logged with timestamps, device state, sample IDs

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────┐
│             Flask Application                       │
├─────────────────────────────────────────────────────┤
│ POST /api/simulate (receives Workflow + Scenario)   │
│ GET /api/simulation/{run_id}/events                 │
│ GET /api/simulation/{run_id}/summary                │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│        Simulation Orchestration Layer               │
├─────────────────────────────────────────────────────┤
│ WorkflowValidator (JSON schema validation)          │
│ ScenarioValidator (sample entry pattern validation) │
│ SimulationEngine (coordinates SimPy execution)      │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│          SimPy Discrete-Event Model                 │
├─────────────────────────────────────────────────────┤
│ Environment (global event queue & clock)            │
│ Device Resources (shared instruments, capacity)     │
│ Sample Processes (individual sample workflows)      │
│ EventLogger (captures all transitions)              │
└─────────────────────────────────────────────────────┘
```

**Data Flow:**
1. Flask receives POST with Workflow JSON + Scenario config
2. Validators check schema compliance and logical consistency
3. SimulationEngine instantiates SimPy environment
4. Sample processes (coroutines) execute, competing for Device resources
5. EventLogger records all state changes with timestamps
6. On completion, Flask returns event timeline + summary statistics

---

## 3. Data Models

### 3.1 Workflow JSON (Input)

**Source:** Your existing schema from `Workflow & Scenario JSON Schema.txt`

Minimal Phase 1a example:

```json
{
  "workflow_id": "single-sample-pcr",
  "workflow_name": "Single Sample PCR",
  "devices": [
    {
      "device_id": "thermal_cycler",
      "device_name": "Thermal Cycler",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    },
    {
      "device_id": "liquid_handler",
      "device_name": "Liquid Handler",
      "resource_capacity": 1,
      "scheduling_policy": "FIFO"
    }
  ],
  "operations": [
    {
      "operation_id": "load_sample",
      "operation_name": "Load Sample",
      "device_id": "liquid_handler",
      "timing": {
        "type": "fixed",
        "value": 5.0
      },
      "operation_type": "setup"
    },
    {
      "operation_id": "dispense_reagent",
      "operation_name": "Dispense Reagent",
      "device_id": "liquid_handler",
      "timing": {
        "type": "triangular",
        "min": 8.0,
        "mode": 10.0,
        "max": 12.0
      },
      "operation_type": "processing"
    },
    {
      "operation_id": "amplify",
      "operation_name": "PCR Amplification",
      "device_id": "thermal_cycler",
      "timing": {
        "type": "exponential",
        "mean": 3600.0
      },
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
      "operation_id": "dispense_reagent",
      "predecessors": ["load_sample"]
    },
    {
      "sequence_id": 3,
      "operation_id": "amplify",
      "predecessors": ["dispense_reagent"]
    }
  ]
}
```

### 3.2 Scenario Configuration (Input)

Defines how samples enter and flow through the workflow.

```json
{
  "scenario_id": "pcr-single-sample",
  "scenario_name": "Single Sample PCR Run",
  "workflow_id": "single-sample-pcr",
  "sample_entry_pattern": {
    "pattern_type": "synchronized",
    "num_samples": 1
  },
  "simulation_config": {
    "random_seed": 42,
    "max_simulation_time": 7200.0
  }
}
```

**Pattern Types (Phase 1a):**

- `synchronized`: All N samples enter at time 0 (synchronized batch)
- `single`: One sample enters at time 0, completes workflow, exits (simplest case)

**Future Patterns (Phase 1c):**
- `staggered`: Samples enter at regular intervals
- `periodic`: Continuous arrival with inter-arrival distribution
- `custom`: Explicit entry times per sample

### 3.3 Event Log Entry

Internal structure for each event recorded during simulation.

```python
@dataclass
class SimulationEvent:
    timestamp: float              # Simulation clock time (seconds)
    event_type: str              # "QUEUED", "START", "COMPLETE", "RELEASED"
    sample_id: str               # "SAMPLE_001"
    operation_id: str            # "dispense_reagent"
    device_id: str               # "liquid_handler"
    duration: float              # Actual sampled duration (seconds)
    wait_time: float             # Time spent waiting for device (seconds)
    device_queue_length: int     # Length of device queue when operation started
    notes: str                   # Optional context
```

**Event Types:**
- `QUEUED`: Sample enters device queue (waiting to acquire resource)
- `START`: Sample acquires device, operation begins
- `COMPLETE`: Operation finishes, device released
- `RELEASED`: Sample released from device

### 3.4 Summary Statistics (Output)

```python
@dataclass
class SimulationSummary:
    total_simulation_time: float
    num_samples_completed: int
    num_samples_failed: int
    
    # Per-device statistics
    device_utilization: Dict[str, float]  # device_id -> utilization %
    device_queue_stats: Dict[str, Dict]   # device_id -> {max_queue_length, avg_queue_time}
    
    # Per-operation statistics
    operation_stats: Dict[str, Dict]      # operation_id -> {mean_duration, stdev_duration, min, max, samples}
    operation_wait_times: Dict[str, Dict] # operation_id -> {mean_wait, total_wait_events}
    
    # Workflow statistics
    total_throughput: float               # samples completed / total_simulation_time
    mean_sample_cycle_time: float         # Average time from entry to exit
    bottleneck_device: str                # Device with highest utilization
    bottleneck_utilization: float         # Utilization % of bottleneck device
```

---

## 4. Core Python Classes

### 4.1 WorkflowValidator

Validates that input Workflow JSON conforms to schema and is logically consistent.

```python
class WorkflowValidator:
    """Validate workflow JSON against schema and logical constraints."""
    
    def validate(self, workflow: dict) -> ValidationResult:
        """
        Returns ValidationResult with:
        - is_valid: bool
        - errors: List[str] (if any)
        - warnings: List[str] (if any)
        """
        # Check schema compliance (use jsonschema library)
        # Check all device_ids referenced in operations exist
        # Check all operation_ids referenced in base_sequence exist
        # Check base_sequence forms valid DAG (no circular predecessors)
        # Check all timing models are properly formed
        # Return ValidationResult
```

**Validation Rules:**

1. **Schema compliance** - Every required field present, correct types
2. **Resource references** - All device_ids in operations match devices[] list
3. **Operation references** - All operation_ids in base_sequence match operations[] list
4. **DAG validity** - No circular predecessor chains (operation A → B → A)
5. **Timing validity** - For triangular: min ≤ mode ≤ max; all values ≥ 0
6. **Capacity validity** - device resource_capacity ≥ 1

### 4.2 ScenarioValidator

Validates scenario configuration and sample entry patterns.

```python
class ScenarioValidator:
    """Validate scenario configuration."""
    
    def validate(self, scenario: dict, workflow: dict) -> ValidationResult:
        """
        Returns ValidationResult with errors/warnings.
        """
        # Check scenario.workflow_id matches provided workflow
        # Check sample_entry_pattern is valid (known pattern_type)
        # For synchronized: num_samples ≥ 1
        # For single: num_samples == 1
        # Check simulation_config has valid random_seed and max_time
```

### 4.3 SimulationEngine

Orchestrates SimPy execution. Core class managing environment, resources, and sample processes.

```python
class SimulationEngine:
    """Execute discrete-event simulation using SimPy."""
    
    def __init__(self, workflow: dict, scenario: dict):
        self.workflow = workflow
        self.scenario = scenario
        self.env = simpy.Environment()
        self.event_log: List[SimulationEvent] = []
        self.resources: Dict[str, simpy.Resource] = {}
        
    def initialize_resources(self):
        """Create SimPy Resource for each device in workflow."""
        for device in self.workflow['devices']:
            capacity = device['resource_capacity']
            self.resources[device['device_id']] = simpy.Resource(
                self.env, 
                capacity=capacity
            )
    
    def run(self) -> Tuple[List[SimulationEvent], SimulationSummary]:
        """Execute simulation and return event log + statistics."""
        self.initialize_resources()
        
        # Determine sample entry times based on pattern
        entry_times = self._compute_entry_times()
        
        # Start sample process for each sample
        for sample_id, entry_time in entry_times:
            self.env.process(
                self._sample_process(sample_id, entry_time)
            )
        
        # Run simulation to completion or max_time
        max_time = self.scenario['simulation_config'].get('max_simulation_time', 86400)
        self.env.run(until=max_time)
        
        # Compute summary statistics
        summary = self._compute_summary()
        
        return self.event_log, summary
    
    def _compute_entry_times(self) -> List[Tuple[str, float]]:
        """
        Compute (sample_id, entry_time) tuples based on sample_entry_pattern.
        
        For synchronized: all samples at t=0
        For single: one sample at t=0
        """
        pattern = self.scenario['sample_entry_pattern']
        num_samples = pattern.get('num_samples', 1)
        
        if pattern['pattern_type'] in ['synchronized', 'single']:
            return [(f"SAMPLE_{i:03d}", 0.0) for i in range(num_samples)]
        else:
            raise ValueError(f"Pattern {pattern['pattern_type']} not supported in Phase 1a")
    
    def _sample_process(self, sample_id: str, entry_time: float):
        """
        Generator function (coroutine) for a single sample's workflow.
        SimPy will interleave execution across all samples.
        """
        # Yield event to wait until entry time
        yield self.env.timeout(entry_time)
        
        # Process each operation in base_sequence
        for step in self.workflow['base_sequence']:
            operation_id = step['operation_id']
            
            # Find operation definition
            op_def = next(
                (op for op in self.workflow['operations'] 
                 if op['operation_id'] == operation_id),
                None
            )
            
            if not op_def:
                raise ValueError(f"Operation {operation_id} not found in workflow")
            
            device_id = op_def['device_id']
            device_resource = self.resources[device_id]
            
            # Wait for predecessors to complete (if any)
            # [Phase 1a: assume linear sequence; handle DAG in Phase 1b]
            
            # Record QUEUED event
            queue_len = len(device_resource.queue)
            self.event_log.append(SimulationEvent(
                timestamp=self.env.now,
                event_type="QUEUED",
                sample_id=sample_id,
                operation_id=operation_id,
                device_id=device_id,
                duration=0.0,
                wait_time=0.0,
                device_queue_length=queue_len,
                notes=""
            ))
            
            # Acquire device resource
            queue_start_time = self.env.now
            with device_resource.request() as req:
                yield req
                
                wait_time = self.env.now - queue_start_time
                
                # Record START event
                self.event_log.append(SimulationEvent(
                    timestamp=self.env.now,
                    event_type="START",
                    sample_id=sample_id,
                    operation_id=operation_id,
                    device_id=device_id,
                    duration=0.0,
                    wait_time=wait_time,
                    device_queue_length=0,
                    notes=""
                ))
                
                # Sample operation duration based on timing model
                duration = self._sample_timing(op_def['timing'])
                
                # Yield timeout for operation duration
                yield self.env.timeout(duration)
                
                # Record COMPLETE event
                self.event_log.append(SimulationEvent(
                    timestamp=self.env.now,
                    event_type="COMPLETE",
                    sample_id=sample_id,
                    operation_id=operation_id,
                    device_id=device_id,
                    duration=duration,
                    wait_time=wait_time,
                    device_queue_length=0,
                    notes=""
                ))
    
    def _sample_timing(self, timing_model: dict) -> float:
        """
        Sample operation duration from timing model.
        Supports: fixed, triangular, exponential
        """
        timing_type = timing_model['type']
        
        if timing_type == 'fixed':
            return timing_model['value']
        
        elif timing_type == 'triangular':
            min_val = timing_model['min']
            mode_val = timing_model['mode']
            max_val = timing_model['max']
            # Use numpy.random.triangular
            return np.random.triangular(min_val, mode_val, max_val)
        
        elif timing_type == 'exponential':
            mean = timing_model['mean']
            # Exponential with given mean
            return np.random.exponential(mean)
        
        else:
            raise ValueError(f"Timing type {timing_type} not supported")
    
    def _compute_summary(self) -> SimulationSummary:
        """
        Analyze event log and compute summary statistics.
        """
        # Group events by device, operation, sample
        # Calculate utilization, queue times, cycle times
        # Identify bottleneck device
        # Return SimulationSummary dataclass
```

### 4.4 EventLogger

Helper class for structured event recording.

```python
class EventLogger:
    """Manages event log for simulation."""
    
    def __init__(self):
        self.events: List[SimulationEvent] = []
    
    def record(self, event: SimulationEvent):
        """Add event to log."""
        self.events.append(event)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert event log to pandas DataFrame for analysis."""
        return pd.DataFrame([asdict(event) for event in self.events])
    
    def export_json(self) -> str:
        """Export event log as JSON."""
        return json.dumps([asdict(event) for event in self.events], default=str)
```

---

## 5. Flask API Endpoints

### 5.1 POST /api/simulate

**Request:**

```json
{
  "workflow": { /* full workflow JSON */ },
  "scenario": { /* full scenario JSON */ }
}
```

**Response (on success):**

```json
{
  "run_id": "sim_run_20250126_001",
  "status": "completed",
  "execution_time_sec": 0.247,
  "event_count": 18,
  "summary": { /* SimulationSummary */ }
}
```

**Response (on validation error):**

```json
{
  "status": "validation_error",
  "errors": [
    "Device 'thermal_cycler' referenced in operation 'amplify' but not defined in devices[]",
    "Circular dependency in base_sequence: operation_id 'step_a' has predecessor 'step_b' which has predecessor 'step_a'"
  ]
}
```

### 5.2 GET /api/simulation/{run_id}/events

**Response:**

```json
{
  "run_id": "sim_run_20250126_001",
  "events": [
    {
      "timestamp": 0.0,
      "event_type": "QUEUED",
      "sample_id": "SAMPLE_000",
      "operation_id": "load_sample",
      "device_id": "liquid_handler",
      "duration": 0.0,
      "wait_time": 0.0,
      "device_queue_length": 0,
      "notes": ""
    },
    /* ... more events ... */
  ]
}
```

### 5.3 GET /api/simulation/{run_id}/summary

**Response:**

```json
{
  "run_id": "sim_run_20250126_001",
  "total_simulation_time": 3847.32,
  "num_samples_completed": 2,
  "device_utilization": {
    "liquid_handler": 0.87,
    "thermal_cycler": 0.95
  },
  "device_queue_stats": {
    "thermal_cycler": {
      "max_queue_length": 1,
      "avg_queue_time": 145.3
    }
  },
  "bottleneck_device": "thermal_cycler",
  "bottleneck_utilization": 0.95
}
```

---

## 6. Test Cases

### 6.1 Unit Tests

**Test: Single Sample, Single Device, Fixed Timing**

```python
def test_single_sample_fixed_timing():
    workflow = {
        "workflow_id": "simple",
        "devices": [{
            "device_id": "dev1",
            "device_name": "Device 1",
            "resource_capacity": 1,
            "scheduling_policy": "FIFO"
        }],
        "operations": [{
            "operation_id": "op1",
            "operation_name": "Op 1",
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
    
    scenario = {
        "scenario_id": "test",
        "workflow_id": "simple",
        "sample_entry_pattern": {"pattern_type": "single", "num_samples": 1},
        "simulation_config": {"random_seed": 42, "max_simulation_time": 100}
    }
    
    engine = SimulationEngine(workflow, scenario)
    events, summary = engine.run()
    
    # Total simulation time should be ~10 seconds (1 sample × 10 sec operation)
    assert abs(summary.total_simulation_time - 10.0) < 0.1
    assert summary.num_samples_completed == 1
    assert len(events) > 0
```

**Test: Synchronized Batch, Device Contention**

```python
def test_synchronized_batch_contention():
    # 2 samples entering at t=0, single device
    # Should see queuing: sample 1 immediate, sample 2 waits
    
    workflow = { /* ... */ }
    scenario = {
        "sample_entry_pattern": {"pattern_type": "synchronized", "num_samples": 2},
        "simulation_config": {"random_seed": 42}
    }
    
    engine = SimulationEngine(workflow, scenario)
    events, summary = engine.run()
    
    # Sample 2 should have non-zero wait time
    sample_2_queued = [e for e in events if e.sample_id == "SAMPLE_001" and e.event_type == "QUEUED"]
    sample_2_start = [e for e in events if e.sample_id == "SAMPLE_001" and e.event_type == "START"]
    
    assert len(sample_2_start) > 0
    assert sample_2_start[0].wait_time > 0  # Should have waited for device
```

**Test: Timing Distribution Sampling**

```python
def test_triangular_timing_distribution():
    # Run simulation 100 times, collect operation durations
    # Verify distribution matches triangular parameters
    
    durations = []
    for _ in range(100):
        engine = SimulationEngine(workflow_with_triangular, scenario)
        events, _ = engine.run()
        op_complete = [e for e in events if e.event_type == "COMPLETE"][0]
        durations.append(op_complete.duration)
    
    # Check bounds: all durations should be within [min, max]
    assert all(8.0 <= d <= 12.0 for d in durations)
    # Check mode: mode should be most common bin
    # (This is a loose check; full statistical test in Phase 1c)
```

**Test: Validation Catches Circular Dependency**

```python
def test_circular_dependency_rejected():
    workflow_with_cycle = {
        "base_sequence": [
            {"sequence_id": 1, "operation_id": "op_a", "predecessors": ["op_b"]},
            {"sequence_id": 2, "operation_id": "op_b", "predecessors": ["op_a"]}
        ]
    }
    
    validator = WorkflowValidator()
    result = validator.validate(workflow_with_cycle)
    
    assert not result.is_valid
    assert any("circular" in err.lower() for err in result.errors)
```

**Test: Validation Catches Missing Device Reference**

```python
def test_missing_device_reference_rejected():
    workflow_bad_ref = {
        "devices": [{"device_id": "dev1", ...}],
        "operations": [{"operation_id": "op1", "device_id": "dev_missing", ...}]
    }
    
    validator = WorkflowValidator()
    result = validator.validate(workflow_bad_ref)
    
    assert not result.is_valid
    assert any("dev_missing" in err for err in result.errors)
```

### 6.2 Integration Tests

**Test: End-to-End Single Sample PCR Workflow**

Use the PCR example from your Intermediate Workflow format. Feed JSON into Flask endpoint, verify events match expected sequence, verify statistics are reasonable.

**Test: Synchronized Batch with Multiple Devices**

2 samples, 3 operations, 2 shared devices. Verify proper queuing and resource scheduling.

---

## 7. Implementation Roadmap

**Week 1: Core Classes**
- WorkflowValidator + schema compliance tests
- ScenarioValidator + pattern validation tests
- Timing distribution sampling (_sample_timing method)

**Week 2: SimPy Integration**
- Initialize SimPy environment + resources
- Implement _sample_process coroutine for linear sequence
- Implement event logging in core loop
- Test single-sample, single-device workflows

**Week 3: Statistics & API**
- Implement _compute_summary() for bottleneck analysis
- Flask endpoints: POST /api/simulate, GET /api/simulation/{run_id}/events, GET /api/simulation/{run_id}/summary
- Integration tests with PCR and multi-device workflows
- Optimize for performance (simulate 1000-sample batch in <5 sec)

**Deliverable:**
- Python package with simulation engine
- Flask API running locally on internal server
- Test suite with >90% code coverage
- Phase 1a complete: validated JSON input → event log + summary statistics

---

## 8. Known Limitations (Phase 1a)

- **DAG handling:** Phase 1a assumes linear sequence (each operation has ≤1 predecessor). Phase 1b will support arbitrary DAGs with parallel branches.
- **Resource constraints:** No consumable inventory tracking, no conditional cleaning logic. Phase 1b feature.
- **Sample exit:** Samples are implicitly removed after base_sequence completes. Phase 1c will model waste collection, result retrieval.
- **Arrival patterns:** Only synchronized and single. Staggered/continuous in Phase 1c.
- **No visualization:** Raw events + statistics only. Plotly integration in Phase 1d.

---

## 9. Dependencies

```
simpy >= 4.0.1           # Discrete-event simulation
numpy >= 1.21            # Statistical distributions
pandas >= 1.3            # Data analysis (event log to dataframe)
flask >= 2.0             # Web API
jsonschema >= 4.0        # JSON schema validation
pydantic >= 1.8          # Data validation (optional, for more structured validation)
```

---

## 10. Acceptance Criteria

Phase 1a is complete when:

1. ✅ WorkflowValidator rejects workflows with circular dependencies, missing device references, invalid timing models
2. ✅ ScenarioValidator accepts synchronized and single entry patterns, rejects invalid configurations
3. ✅ SimulationEngine produces event logs with correct timestamps, device contention, queue wait times
4. ✅ Statistics accurately identify bottleneck device (highest utilization) and queue delays
5. ✅ Flask API accepts JSON, returns validated event log + summary in <1 sec for 10-sample batch
6. ✅ All timing distributions (fixed, triangular, exponential) sample correctly and deterministically with seed
7. ✅ Test suite covers single-device, multi-device, synchronized batch, and validation failure cases
8. ✅ Documentation includes example workflows, API usage, and test methodology

---

## 11. Questions for Team

1. **Database requirement:** Should simulation runs be persisted to a database (SQLite, PostgreSQL) or kept in-memory during Phase 1a? Recommend: SQLite locally for simplicity, migrate to proper DB in Phase 1c.

2. **Random seed handling:** Should users provide random_seed in scenario config (for reproducibility), or always generate random results? Recommend: allow optional seed, default to time-based if not provided.

3. **Event filtering:** Should GET /api/simulation/{run_id}/events support filtering by sample_id, operation_id, or device_id? Recommend: implement in Phase 1b once basic API is solid.

4. **Performance targets:** Any targets for simulation speed? Recommend: aim for 100-sample, 20-operation workflow to complete in <2 sec on typical hardware.

5. **Error handling:** For simulation failures (e.g., infinite wait), what should engine do? Recommend: set max_simulation_time as hard timeout, return partial results + warning.

