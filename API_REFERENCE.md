# Phase 1a API Reference

## Overview

Flask REST API for submitting workflows and scenarios, executing simulations, and retrieving results.

**Base URL:** `http://localhost:5000` (local development)

---

## Endpoints

### 1. POST /api/simulate

Execute a discrete-event simulation with provided workflow and scenario.

**URL:** `/api/simulate`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body

```json
{
  "workflow": {
    "workflow_id": "string",
    "workflow_name": "string",
    "devices": [ /* ... */ ],
    "operations": [ /* ... */ ],
    "base_sequence": [ /* ... */ ]
  },
  "scenario": {
    "scenario_id": "string",
    "workflow_id": "string",
    "sample_entry_pattern": {
      "pattern_type": "synchronized|single",
      "num_samples": integer
    },
    "simulation_config": {
      "random_seed": integer,
      "max_simulation_time": number
    }
  }
}
```

#### Response: Success (200 OK)

```json
{
  "status": "success",
  "run_id": "sim_run_20250126_001",
  "execution_time_sec": 0.247,
  "event_count": 18,
  "summary": {
    "total_simulation_time": 3613.0,
    "num_samples_completed": 1,
    "num_samples_failed": 0,
    "device_utilization": {
      "liquid_handler": 0.0036,
      "thermal_cycler": 0.996
    },
    "device_queue_stats": {
      "liquid_handler": {
        "max_queue_length": 0,
        "avg_queue_time": 0.0
      },
      "thermal_cycler": {
        "max_queue_length": 0,
        "avg_queue_time": 0.0
      }
    },
    "operation_stats": {
      "load_sample": {
        "mean_duration": 5.0,
        "stdev_duration": 0.0,
        "min_duration": 5.0,
        "max_duration": 5.0,
        "sample_count": 1
      },
      "add_reagent": {
        "mean_duration": 8.0,
        "stdev_duration": 0.0,
        "min_duration": 8.0,
        "max_duration": 8.0,
        "sample_count": 1
      },
      "amplify": {
        "mean_duration": 3600.0,
        "stdev_duration": 0.0,
        "min_duration": 3600.0,
        "max_duration": 3600.0,
        "sample_count": 1
      }
    },
    "operation_wait_times": {
      "load_sample": {
        "mean_wait": 0.0,
        "total_wait_events": 0
      },
      "add_reagent": {
        "mean_wait": 0.0,
        "total_wait_events": 0
      },
      "amplify": {
        "mean_wait": 0.0,
        "total_wait_events": 0
      }
    },
    "total_throughput": 0.000277,
    "mean_sample_cycle_time": 3613.0,
    "bottleneck_device": "thermal_cycler",
    "bottleneck_utilization": 0.996
  }
}
```

#### Response: Validation Error (400 Bad Request)

```json
{
  "status": "validation_error",
  "errors": [
    "Workflow missing required field 'devices'",
    "Device 'thermal_cycler' referenced in operation 'amplify' but not defined in devices[]",
    "Invalid timing model in operation 'amplify': exponential requires 'mean' parameter"
  ],
  "warnings": []
}
```

#### Response: Execution Error (500 Internal Server Error)

```json
{
  "status": "simulation_error",
  "error_message": "Simulation exceeded max_simulation_time (7200s); results may be incomplete",
  "partial_results": {
    "events_processed": 152,
    "simulation_time_at_failure": 7200.0
  }
}
```

#### Curl Example

```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d @request.json
```

File: `request.json` contains the full workflow + scenario.

---

### 2. GET /api/simulation/{run_id}/events

Retrieve complete event log from a completed simulation.

**URL:** `/api/simulation/{run_id}/events`  
**Method:** `GET`  
**Query Parameters:**
- `sample_id` (optional): Filter events for a specific sample
- `operation_id` (optional): Filter events for a specific operation
- `device_id` (optional): Filter events for a specific device
- `event_type` (optional): Filter by event type (QUEUED, START, COMPLETE, RELEASED)
- `limit` (optional): Maximum number of events to return (default: 1000)
- `offset` (optional): Pagination offset (default: 0)

#### Response: Success (200 OK)

```json
{
  "status": "success",
  "run_id": "sim_run_20250126_001",
  "filter_applied": {
    "sample_id": null,
    "operation_id": null,
    "device_id": null,
    "event_type": null
  },
  "event_count": 18,
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
    {
      "timestamp": 0.0,
      "event_type": "START",
      "sample_id": "SAMPLE_000",
      "operation_id": "load_sample",
      "device_id": "liquid_handler",
      "duration": 0.0,
      "wait_time": 0.0,
      "device_queue_length": 0,
      "notes": ""
    },
    {
      "timestamp": 5.0,
      "event_type": "COMPLETE",
      "sample_id": "SAMPLE_000",
      "operation_id": "load_sample",
      "device_id": "liquid_handler",
      "duration": 5.0,
      "wait_time": 0.0,
      "device_queue_length": 0,
      "notes": ""
    }
  ]
}
```

#### Curl Example

```bash
# Get all events
curl http://localhost:5000/api/simulation/sim_run_20250126_001/events

# Filter by sample
curl "http://localhost:5000/api/simulation/sim_run_20250126_001/events?sample_id=SAMPLE_000"

# Filter by device and limit results
curl "http://localhost:5000/api/simulation/sim_run_20250126_001/events?device_id=thermal_cycler&limit=50"

# Filter by event type (queue delays)
curl "http://localhost:5000/api/simulation/sim_run_20250126_001/events?event_type=QUEUED"
```

---

### 3. GET /api/simulation/{run_id}/summary

Retrieve summary statistics from a completed simulation.

**URL:** `/api/simulation/{run_id}/summary`  
**Method:** `GET`

#### Response: Success (200 OK)

```json
{
  "status": "success",
  "run_id": "sim_run_20250126_001",
  "summary": {
    "total_simulation_time": 3613.0,
    "num_samples_completed": 1,
    "num_samples_failed": 0,
    "device_utilization": {
      "liquid_handler": 0.0036,
      "thermal_cycler": 0.996
    },
    "device_queue_stats": {
      "liquid_handler": {
        "max_queue_length": 0,
        "avg_queue_time": 0.0,
        "total_queue_time": 0.0,
        "queue_events": 0
      },
      "thermal_cycler": {
        "max_queue_length": 0,
        "avg_queue_time": 0.0,
        "total_queue_time": 0.0,
        "queue_events": 0
      }
    },
    "operation_stats": {
      "load_sample": {
        "mean_duration": 5.0,
        "stdev_duration": 0.0,
        "min_duration": 5.0,
        "max_duration": 5.0,
        "median_duration": 5.0,
        "sample_count": 1
      },
      "add_reagent": {
        "mean_duration": 8.0,
        "stdev_duration": 0.0,
        "min_duration": 8.0,
        "max_duration": 8.0,
        "median_duration": 8.0,
        "sample_count": 1
      },
      "amplify": {
        "mean_duration": 3600.0,
        "stdev_duration": 0.0,
        "min_duration": 3600.0,
        "max_duration": 3600.0,
        "median_duration": 3600.0,
        "sample_count": 1
      }
    },
    "operation_wait_times": {
      "load_sample": {
        "mean_wait": 0.0,
        "total_wait": 0.0,
        "wait_events": 0
      },
      "add_reagent": {
        "mean_wait": 0.0,
        "total_wait": 0.0,
        "wait_events": 0
      },
      "amplify": {
        "mean_wait": 0.0,
        "total_wait": 0.0,
        "wait_events": 0
      }
    },
    "total_throughput": 0.000277,
    "mean_sample_cycle_time": 3613.0,
    "min_sample_cycle_time": 3613.0,
    "max_sample_cycle_time": 3613.0,
    "bottleneck_device": "thermal_cycler",
    "bottleneck_utilization": 0.996,
    "bottleneck_queue_delay": 0.0
  }
}
```

#### Curl Example

```bash
curl http://localhost:5000/api/simulation/sim_run_20250126_001/summary
```

---

## Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 200 | Success | Simulation completed and results retrieved |
| 400 | Bad Request | Validation error in workflow or scenario JSON |
| 404 | Not Found | run_id does not exist in database |
| 422 | Unprocessable Entity | Schema valid but logically inconsistent (e.g., circular dependency) |
| 500 | Internal Server Error | Simulation execution failed or database error |

---

## Rate Limiting (Future)

Phase 1c will implement rate limiting. Phase 1a has no limits.

---

## Example Workflow: Using the API

### Step 1: Prepare workflow and scenario

```json
// workflow.json - same as Example 1 from EXAMPLE_WORKFLOWS.md
{
  "workflow_id": "single-sample-pcr-minimal",
  ...
}

// scenario.json
{
  "scenario_id": "pcr-single-sample-run1",
  ...
}
```

### Step 2: Submit simulation request

```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": { /* workflow content */ },
    "scenario": { /* scenario content */ }
  }' \
  | jq '.' > response.json
```

### Step 3: Extract run_id from response

```bash
run_id=$(jq -r '.run_id' response.json)
echo "Simulation run ID: $run_id"
```

### Step 4: Retrieve events

```bash
curl "http://localhost:5000/api/simulation/$run_id/events?limit=50" \
  | jq '.events | .[] | {timestamp, event_type, operation_id, wait_time}' > events.json
```

### Step 5: Retrieve summary

```bash
curl "http://localhost:5000/api/simulation/$run_id/summary" \
  | jq '.summary | {bottleneck_device, bottleneck_utilization, total_throughput}' > summary.json
```

---

## Data Types

### DeviceUtilization (Dict[str, float])

```
{
  "device_id": utilization_percentage (0.0 to 1.0)
}
```

Example: `{"thermal_cycler": 0.95, "liquid_handler": 0.08}`

### QueueStats (Dict[str, Dict])

```
{
  "device_id": {
    "max_queue_length": integer,
    "avg_queue_time": float (seconds),
    "total_queue_time": float (seconds),
    "queue_events": integer
  }
}
```

Example:
```json
{
  "analyzer": {
    "max_queue_length": 3,
    "avg_queue_time": 145.3,
    "total_queue_time": 581.2,
    "queue_events": 4
  }
}
```

### OperationStats (Dict[str, Dict])

```
{
  "operation_id": {
    "mean_duration": float (seconds),
    "stdev_duration": float (seconds),
    "min_duration": float (seconds),
    "max_duration": float (seconds),
    "median_duration": float (seconds),
    "sample_count": integer
  }
}
```

---

## Testing the API

### Manual Testing with Postman

1. Create new POST request to `http://localhost:5000/api/simulate`
2. Set Body → raw → JSON
3. Paste complete workflow + scenario JSON
4. Click Send
5. Copy run_id from response
6. Create GET requests to events and summary endpoints with run_id

### Automated Testing with pytest

See `CODING_GUIDELINES.md` section "Test File Organization" for unit test structure.

Example integration test:

```python
import json
import pytest
from api.routes import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_post_simulate_single_sample(client):
    workflow = { /* ... */ }
    scenario = { /* ... */ }
    
    response = client.post(
        '/api/simulate',
        data=json.dumps({"workflow": workflow, "scenario": scenario}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'run_id' in data
    assert 'summary' in data
```

---

## Future API Endpoints (Phase 1b+)

- `POST /api/workflows` - Save workflow template
- `GET /api/workflows/{workflow_id}` - Retrieve saved workflow
- `POST /api/scenarios` - Save scenario template
- `GET /api/scenarios/{scenario_id}` - Retrieve saved scenario
- `GET /api/simulation/{run_id}/statistics` - Advanced analytics
- `GET /api/simulation/{run_id}/export` - Export events as CSV/Excel

