# Modular Instrument Workflow Simulator - Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend UI (React)                      │
│  - Workflow canvas (DAG editor)                             │
│  - Property panels (devices, operations)                    │
│  - Simulation control & results panels                      │
└─────────────────────┬───────────────────────────────────────┘
                      │ JSON workflow definition
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              REST API Layer (FastAPI/Flask)                  │
│  - /workflows (CRUD)                                         │
│  - /simulations (execute, retrieve results)                 │
│  - /visualizations (render, export)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│    Core      │ │  Simulation  │ │ Visualization    │
│   Engine     │ │  Backends    │ │    Backends      │
│  (Workflow   │ │              │ │                  │
│  Validator,  │ │  ├─ SimPy    │ │  ├─ Plotly       │
│  Executor)   │ │  ├─ Simulus  │ │  ├─ Chart.js     │
│              │ │  └─ Custom   │ │  └─ Custom       │
└──────────────┘ └──────────────┘ └──────────────────┘
```

## Core Components

### 1. Core Engine (`core/`)
Language-agnostic simulation control layer that:
- Validates workflow JSON schema
- Orchestrates simulation execution
- Manages simulation state and lifecycle
- Produces standardized event logs

**Key Responsibility:** Convert validated workflow → standardized event log (independent of backend choice)

### 2. Simulation Backend Interface (`simulators/base.py`)

All simulation backends implement a common interface:

```python
class SimulationBackend(ABC):
    """Abstract base class for all simulation backends."""
    
    def __init__(self, workflow_definition: dict):
        """Initialize with validated workflow JSON."""
        self.workflow = workflow_definition
    
    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate workflow is compatible with this backend.
        Returns: (is_valid, list_of_errors)
        """
        pass
    
    @abstractmethod
    def execute(self, until_time: float = None) -> EventLog:
        """
        Execute simulation and return standardized event log.
        """
        pass
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return backend identifier (e.g., 'simpy', 'simulus')."""
        pass
```

### 3. Simulation Backends

#### SimPy Backend (`simulators/simpy_backend.py`)

```python
class SimPyBackend(SimulationBackend):
    def validate(self) -> tuple[bool, list[str]]:
        # Check device/operation references, detect cycles, etc.
        pass
    
    def execute(self, until_time: float = None) -> EventLog:
        # Instantiate SimPy Environment
        # Create Device resources and Workstream processes
        # Run simulation
        # Extract and normalize events to EventLog schema
        pass
```

#### Pluggable Alternative Backends
Future implementations (Simulus, custom, etc.) follow the same interface.

### 4. Event Log Standardization (`core/event_log.py`)

All backends produce a **standardized EventLog** object:

```python
@dataclass
class SimulationEvent:
    timestamp: float
    event_type: str  # operation_start, operation_complete, etc.
    operation_id: str
    device_id: str
    workstream_id: str
    details: dict  # Backend-specific metadata

@dataclass
class EventLog:
    simulation_run_id: str
    workflow_definition: dict
    events: list[SimulationEvent]
    simulation_statistics: dict
    backend_name: str
    execution_time_wall_clock: float
```

### 5. Visualization Backend Interface (`visualizers/base.py`)

```python
class VisualizationBackend(ABC):
    """Abstract base class for all visualization backends."""
    
    def __init__(self, event_log: EventLog):
        self.event_log = event_log
    
    @abstractmethod
    def render_gantt(self) -> str:
        """
        Render Gantt chart.
        Returns: HTML/JSON representation.
        """
        pass
    
    @abstractmethod
    def render_utilization(self) -> str:
        """Render resource utilization graph."""
        pass
    
    @abstractmethod
    def render_queue_length(self) -> str:
        """Render queue length time-series."""
        pass
    
    @abstractmethod
    def export(self, format: str) -> bytes:
        """Export visualization (PNG, PDF, SVG)."""
        pass
    
    @property
    @abstractmethod
    def backend_name(self) -> str:
        pass
```

### 6. Visualization Backends

#### Plotly Backend (`visualizers/plotly_backend.py`)

```python
class PlotlyBackend(VisualizationBackend):
    def render_gantt(self) -> str:
        # Parse event_log
        # Build Plotly Figure with timeline bars per device
        # Return as JSON/HTML
        pass
    
    def render_utilization(self) -> str:
        # Compute device capacity utilization over time
        # Generate Plotly line chart
        pass
```

#### Chart.js Backend (`visualizers/chartjs_backend.py`)
Follows same interface, uses Chart.js library for rendering.

### 7. API Layer (`api/`)

FastAPI endpoints wire components together:

```python
@app.post("/api/simulations")
def run_simulation(
    workflow_definition: dict,
    simulator_backend: str = "simpy",  # Route selection
    visualizer_backend: str = "plotly"
) -> SimulationResult:
    # 1. Validate workflow
    # 2. Instantiate selected SimulationBackend class
    # 3. Execute simulation → EventLog
    # 4. Instantiate selected VisualizationBackend
    # 5. Render visualizations
    # 6. Return results
    pass

@app.get("/api/simulations/{simulation_id}/gantt")
def get_gantt(simulation_id: str, format: str = "html"):
    # Retrieve cached EventLog
    # Use visualizer_backend from simulation metadata
    # Return visualization
    pass
```

## Module Organization

```
instrument-workflow-sim/
├── backend/
│   ├── core/
│   │   ├── workflow_validator.py
│   │   ├── event_log.py
│   │   └── executor.py
│   ├── simulators/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract SimulationBackend
│   │   ├── simpy_backend.py        # Default implementation
│   │   └── simulus_backend.py      # Future alternative
│   ├── visualizers/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract VisualizationBackend
│   │   ├── plotly_backend.py       # Default implementation
│   │   └── chartjs_backend.py      # Future alternative
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowCanvas.jsx
│   │   │   ├── PropertyPanel.jsx
│   │   │   └── ResultsPanel.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.jsx
│   └── package.json
└── docker-compose.yml
```

## Backend Selection Mechanism

### Runtime Selection
```python
# api/routes.py
def get_simulation_backend(backend_name: str) -> SimulationBackend:
    registry = {
        "simpy": SimPyBackend,
        "simulus": SimulusBackend,
        # Register new backends here
    }
    return registry[backend_name]

def get_visualization_backend(backend_name: str) -> VisualizationBackend:
    registry = {
        "plotly": PlotlyBackend,
        "chartjs": ChartJsBackend,
    }
    return registry[backend_name]
```

### Configuration
```yaml
# config.yaml
defaults:
  simulation_backend: "simpy"
  visualization_backend: "plotly"
  
available_backends:
  simulation:
    - simpy
    - simulus
  visualization:
    - plotly
    - chartjs
```

## Extension Points (Future Backends)

To add a new simulation backend:
1. Create `simulators/new_backend.py`
2. Implement `SimulationBackend` ABC
3. Register in `get_simulation_backend()` registry
4. No changes to frontend, API, or core logic needed

Same process for visualization backends.

## Data Flow Example

**User Action:** "Run simulation with SimPy, visualize with Plotly"

1. Frontend sends: `POST /api/simulations { workflow_json, simulator_backend: "simpy", visualizer_backend: "plotly" }`
2. API layer:
   - Validates workflow
   - Calls `SimPyBackend(workflow).execute()` → EventLog
   - Calls `PlotlyBackend(event_log).render_gantt()` → HTML/JSON
   - Caches EventLog for future requests
   - Returns visualization + statistics
3. Frontend renders interactive results

**Switch Backend:** Same workflow, different backends → no re-validation needed, just re-execute

## Advantages of This Architecture

- **Loose Coupling:** Frontned, API, and backends are independent
- **Testability:** Each backend can be unit tested in isolation
- **Extensibility:** New backends require no changes to existing code
- **Vendor Agnostic:** Can compare SimPy vs. Simulus results directly
- **Future-Proof:** Supports stochastic distributions, continuous simulation, or other future enhancements by adding backends