# Instrument Workflow Simulator - Claude Code Context

**Project:** Discrete-event simulation application for diagnostic/clinical chemistry instrument workflow timing analysis.

**Tech Stack:** Flask (Python backend), React (frontend), SimPy (default simulation engine), Plotly (default visualization), Railway (production hosting).

**Repository Structure:** Managed via local git + remote repository.

---

## Project Overview

### Purpose
Enable systems engineers to perform timing and resource utilization analysis of instrument workflows via a web-based UI. Engineers define workflows graphically, simulate them with pluggable backends, and visualize results as Gantt charts and resource utilization graphs.

### Scope - Phase 1
- Core Flask API with modular simulation and visualization backends
- Default backends: SimPy + Plotly
- JSON workflow serialization
- Event log standardization
- Containerized deployment (Docker)

---

## Architecture

### High-Level Design
```
Frontend (React) ←→ Flask REST API ←→ Simulation Backends (SimPy, etc.)
                                   ├→ Visualization Backends (Plotly, etc.)
                                   └→ Core Engine (validation, orchestration)
```

### Backend Module Structure
```
instrument-workflow-sim/
├── backend/
│   ├── app.py                          # Flask application factory
│   ├── config.py                       # Configuration management
│   ├── core/
│   │   ├── __init__.py
│   │   ├── workflow_validator.py       # JSON schema validation
│   │   ├── event_log.py                # Standardized event log dataclass
│   │   └── executor.py                 # Simulation orchestration
│   ├── simulators/
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract SimulationBackend
│   │   └── simpy_backend.py            # Default SimPy implementation
│   ├── visualizers/
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract VisualizationBackend
│   │   └── plotly_backend.py           # Default Plotly implementation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                   # Flask blueprints & endpoints
│   │   └── schemas.py                  # Pydantic models for validation
│   ├── utils/
│   │   ├── __init__.py
│   │   └── backend_registry.py         # Backend discovery & registration
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowCanvas.jsx
│   │   │   ├── PropertyPanel.jsx
│   │   │   ├── SimulationPanel.jsx
│   │   │   └── ResultsPanel.jsx
│   │   ├── services/
│   │   │   └── api.js                  # API client
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── ARCHITECTURE.md                     # Detailed architecture (modular design)
└── DEPLOYMENT.md                       # Railway deployment guide

```

---

## Key Design Decisions

### 1. Modular Backends (Critical for extensibility)

**Simulation Backends** implement abstract base class:
```python
class SimulationBackend(ABC):
    def validate(self) -> tuple[bool, list[str]]: pass
    def execute(self, until_time: float = None) -> EventLog: pass
    @property
    def backend_name(self) -> str: pass
```

**Visualization Backends** implement abstract base class:
```python
class VisualizationBackend(ABC):
    def render_gantt(self) -> str: pass
    def render_utilization(self) -> str: pass
    def render_queue_length(self) -> str: pass
    def export(self, format: str) -> bytes: pass
    @property
    def backend_name(self) -> str: pass
```

Adding new backends requires only implementing the interface and registering in `backend_registry.py`.

### 2. Standardized Event Log

All simulation backends produce a common `EventLog` dataclass:
```python
@dataclass
class SimulationEvent:
    timestamp: float
    event_type: str  # operation_start, operation_complete, device_queue_entry, etc.
    operation_id: str
    device_id: str
    workstream_id: str
    details: dict

@dataclass
class EventLog:
    simulation_run_id: str (UUID)
    workflow_definition: dict
    events: list[SimulationEvent]
    simulation_statistics: dict
    backend_name: str
    execution_time_wall_clock: float
```

This decouples simulation engine choice from visualization.

### 3. Workflow JSON Schema

```json
{
  "workflow_name": "string",
  "workflow_version": "string",
  "devices": [
    {
      "device_id": "string",
      "device_name": "string",
      "resource_capacity": integer,
      "scheduling_policy": "FIFO | PRIORITY",
      "priority_ordering": ["operation_id_1", ...]
    }
  ],
  "operations": [
    {
      "operation_id": "string",
      "operation_name": "string",
      "device_id": "string",
      "duration_time": float,
      "operation_type": "processing | setup | teardown",
      "priority": integer,
      "workstream_id": "string"
    }
  ],
  "sequence": [
    {
      "sequence_id": integer,
      "operation_id": "string",
      "predecessors": ["operation_id_1", ...],
      "workstream_id": "string"
    }
  ]
}
```

### 4. Flask API Endpoints

**Core endpoints:**
- `POST /api/workflows` - Validate & store workflow
- `GET /api/workflows/{workflow_id}` - Retrieve workflow
- `POST /api/simulations` - Execute simulation (query params: `simulator_backend=simpy`, `visualizer_backend=plotly`)
- `GET /api/simulations/{simulation_id}` - Retrieve results
- `GET /api/simulations/{simulation_id}/gantt` - Render Gantt chart
- `GET /api/simulations/{simulation_id}/utilization` - Render utilization graph
- `GET /api/backends` - List available simulation/visualization backends

---

## Development Workflow

### Local Setup
```bash
# Clone repository
git clone <remote-repo-url>
cd instrument-workflow-sim

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Run locally (from project root)
docker-compose up
```

### Environment Variables
Create `.env` in backend and frontend:

**Backend (`backend/.env`):**
```
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///simulations.db
DEFAULT_SIMULATION_BACKEND=simpy
DEFAULT_VISUALIZATION_BACKEND=plotly
```

**Frontend (`frontend/.env`):**
```
REACT_APP_API_URL=http://localhost:5000
```

### Git Workflow
- Feature branches: `feature/backend-modularity`, `feature/plotly-viz`, etc.
- Commits should be atomic (single responsibility)
- Push to remote before opening PR/merging to main

---

## Deployment on Railway

### Prerequisites
1. Railway account (railway.app)
2. GitHub repository linked to Railway
3. Docker image builds automatically from root `Dockerfile`

### Railway Configuration

**railway.toml** (at project root):
```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app"
restartPolicyMaxRetries = 5
```

**Environment Variables in Railway Dashboard:**
```
FLASK_ENV=production
DATABASE_URL=postgresql://...  # Railway provides PostgreSQL add-on
DEFAULT_SIMULATION_BACKEND=simpy
DEFAULT_VISUALIZATION_BACKEND=plotly
FLASK_SECRET_KEY=<generated-secret>
```

### Dockerfile (Multi-stage Build)
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY backend .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Deployment Steps
1. Push to remote: `git push origin main`
2. Railway auto-detects changes via GitHub webhook
3. Builds Docker image and deploys
4. Logs available in Railway dashboard

---

## Testing Strategy

### Unit Tests
- Workflow validator: test JSON schema validation, cycle detection
- SimPy backend: mock environment, verify event log structure
- Plotly backend: verify chart JSON output

### Integration Tests
- End-to-end workflow: validate → execute → visualize
- Backend switching: run same workflow with SimPy vs. alternative
- API endpoints: request/response validation

### Test Runner
```bash
cd backend
pytest tests/ -v --cov=.
```

---

## Code Standards

- **Python:** PEP 8, type hints for all functions
- **JavaScript/React:** ESLint configuration, functional components
- **Docstrings:** Google-style docstrings for all public methods
- **Commits:** "feat:", "fix:", "refactor:", "docs:", "test:" prefixes

---

## Performance Targets

- Workflow validation: < 500 ms
- Simulation execution (1,000 operations): < 5 seconds
- Gantt chart rendering: < 2 seconds
- API response time: < 1 second (excluding simulation time)

---

## Extension Points (Future)

1. **Stochastic Timing:** Add backend supporting probability distributions
2. **Database Persistence:** PostgreSQL integration for workflow/simulation history
3. **Batch Runs:** Multiple simulations with parameter sweeps
4. **Authentication:** User accounts, workflow sharing
5. **Alternative Backends:** Simulus, custom DES engine, continuous simulation
6. **Advanced Visualization:** 3D timelines, interactive drill-down, export to PDF/SVG

---

## Critical Files to Reference

- **ARCHITECTURE.md** - Detailed modular design (abstract base classes, plugin registry)
- **requirements.txt** - Dependencies (Flask, SimPy, Plotly, Pydantic, etc.)
- **docker-compose.yml** - Local development orchestration
- **Dockerfile** - Production image build
- **railway.toml** - Railway deployment config

---

## Initial Implementation Order

1. **Phase 1a:** Core engine (workflow validator, EventLog, SimPy backend wrapper)
2. **Phase 1b:** Plotly visualization backend
3. **Phase 1c:** Flask API layer (endpoints, blueprint structure)
4. **Phase 1d:** Frontend canvas & property panels (React components)
5. **Phase 2:** Results visualization panels, Gantt/utilization charts
6. **Phase 3:** Docker & Railway deployment, CI/CD
7. **Phase 4:** Alternative backends (Simulus, Chart.js), advanced features

---

## Key References

- SimPy documentation: https://simpy.readthedocs.io/
- Flask documentation: https://flask.palletsprojects.com/
- Railway documentation: https://docs.railway.app/
- Plotly Python: https://plotly.com/python/
- Pydantic: https://docs.pydantic.dev/