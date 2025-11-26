"""Integration tests for Flask API endpoints."""
import pytest
import json
from main import create_app


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def simple_request_data(simple_workflow, simple_scenario):
    """Create simple request data for API testing."""
    return {
        "workflow": simple_workflow,
        "scenario": simple_scenario
    }


@pytest.fixture
def batch_request_data(multi_device_workflow, synchronized_scenario):
    """Create batch request data for API testing."""
    return {
        "workflow": multi_device_workflow,
        "scenario": synchronized_scenario
    }


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test that health check endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint(self, client):
        """Test that root endpoint returns service info."""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'service' in data
        assert 'endpoints' in data


class TestSimulateEndpoint:
    """Tests for POST /api/simulate endpoint."""

    def test_simulate_single_sample_success(self, client, simple_request_data):
        """Test successful single sample simulation."""
        response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'run_id' in data
        assert data['run_id'].startswith('sim_run_')
        assert 'execution_time_sec' in data
        assert 'event_count' in data
        assert 'summary' in data

        # Check summary structure
        summary = data['summary']
        assert 'total_simulation_time' in summary
        assert 'num_samples_completed' in summary
        assert summary['num_samples_completed'] == 1
        assert 'device_utilization' in summary
        assert 'operation_stats' in summary
        assert 'bottleneck_device' in summary

    def test_simulate_batch_success(self, client, batch_request_data):
        """Test successful batch simulation."""
        response = client.post(
            '/api/simulate',
            data=json.dumps(batch_request_data),
            content_type='application/json'
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['summary']['num_samples_completed'] == 3

    def test_simulate_no_json_data(self, client):
        """Test that missing JSON data returns 400."""
        response = client.post('/api/simulate')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'No JSON data' in data['error_message']

    def test_simulate_missing_workflow(self, client, simple_scenario):
        """Test that missing workflow returns 400."""
        response = client.post(
            '/api/simulate',
            data=json.dumps({"scenario": simple_scenario}),
            content_type='application/json'
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'workflow' in data['error_message'].lower()

    def test_simulate_missing_scenario(self, client, simple_workflow):
        """Test that missing scenario returns 400."""
        response = client.post(
            '/api/simulate',
            data=json.dumps({"workflow": simple_workflow}),
            content_type='application/json'
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'scenario' in data['error_message'].lower()

    def test_simulate_invalid_workflow(self, client, simple_scenario):
        """Test that invalid workflow returns 400 with validation errors."""
        invalid_workflow = {
            "workflow_id": "invalid",
            "devices": [],  # Empty devices list is invalid
            "operations": [],
            "base_sequence": []
        }

        response = client.post(
            '/api/simulate',
            data=json.dumps({
                "workflow": invalid_workflow,
                "scenario": simple_scenario
            }),
            content_type='application/json'
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'validation_error'
        assert 'errors' in data
        assert len(data['errors']) > 0

    def test_simulate_workflow_scenario_mismatch(self, client, simple_workflow, synchronized_scenario):
        """Test that workflow/scenario ID mismatch returns 400."""
        response = client.post(
            '/api/simulate',
            data=json.dumps({
                "workflow": simple_workflow,
                "scenario": synchronized_scenario
            }),
            content_type='application/json'
        )

        assert response.status_code == 400

        data = json.loads(response.data)
        assert data['status'] == 'validation_error'

    def test_simulate_returns_statistics(self, client, simple_request_data):
        """Test that simulation returns comprehensive statistics."""
        response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )

        data = json.loads(response.data)
        summary = data['summary']

        # Check device utilization
        assert 'device_utilization' in summary
        assert isinstance(summary['device_utilization'], dict)
        assert len(summary['device_utilization']) > 0

        # Check operation stats
        assert 'operation_stats' in summary
        assert isinstance(summary['operation_stats'], dict)

        # Check queue stats
        assert 'device_queue_stats' in summary

        # Check bottleneck identification
        assert 'bottleneck_device' in summary
        assert 'bottleneck_utilization' in summary


class TestEventsEndpoint:
    """Tests for GET /api/simulation/{run_id}/events endpoint."""

    def test_get_events_success(self, client, simple_request_data):
        """Test successful event retrieval."""
        # First run a simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get events
        response = client.get(f'/api/simulation/{run_id}/events')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['run_id'] == run_id
        assert 'events' in data
        assert 'event_count' in data
        assert len(data['events']) > 0

        # Check event structure
        event = data['events'][0]
        assert 'timestamp' in event
        assert 'event_type' in event
        assert 'sample_id' in event
        assert 'operation_id' in event
        assert 'device_id' in event

    def test_get_events_not_found(self, client):
        """Test that invalid run_id returns 404."""
        response = client.get('/api/simulation/invalid_run_id/events')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_get_events_with_sample_filter(self, client, batch_request_data):
        """Test event filtering by sample_id."""
        # Run a batch simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(batch_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get events for specific sample
        response = client.get(f'/api/simulation/{run_id}/events?sample_id=SAMPLE_000')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['filter_applied']['sample_id'] == 'SAMPLE_000'

        # All events should be for SAMPLE_000
        for event in data['events']:
            assert event['sample_id'] == 'SAMPLE_000'

    def test_get_events_with_event_type_filter(self, client, simple_request_data):
        """Test event filtering by event_type."""
        # Run simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get only START events
        response = client.get(f'/api/simulation/{run_id}/events?event_type=START')
        assert response.status_code == 200

        data = json.loads(response.data)

        # All events should be START
        for event in data['events']:
            assert event['event_type'] == 'START'

    def test_get_events_with_pagination(self, client, simple_request_data):
        """Test event pagination."""
        # Run simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get first 2 events
        response = client.get(f'/api/simulation/{run_id}/events?limit=2&offset=0')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['event_count'] == 2

        # Get next 2 events
        response2 = client.get(f'/api/simulation/{run_id}/events?limit=2&offset=2')
        data2 = json.loads(response2.data)

        # Events should be different
        if data2['event_count'] > 0:
            assert data['events'][0]['timestamp'] != data2['events'][0]['timestamp'] or \
                   data['events'][0]['event_type'] != data2['events'][0]['event_type']


class TestSummaryEndpoint:
    """Tests for GET /api/simulation/{run_id}/summary endpoint."""

    def test_get_summary_success(self, client, simple_request_data):
        """Test successful summary retrieval."""
        # First run a simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get summary
        response = client.get(f'/api/simulation/{run_id}/summary')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['run_id'] == run_id
        assert 'summary' in data

        # Check summary fields
        summary = data['summary']
        assert 'total_simulation_time' in summary
        assert 'num_samples_completed' in summary
        assert 'device_utilization' in summary
        assert 'operation_stats' in summary
        assert 'bottleneck_device' in summary

    def test_get_summary_not_found(self, client):
        """Test that invalid run_id returns 404."""
        response = client.get('/api/simulation/invalid_run_id/summary')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 'error'

    def test_summary_device_utilization(self, client, simple_request_data):
        """Test that summary contains device utilization."""
        # Run simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get summary
        response = client.get(f'/api/simulation/{run_id}/summary')
        data = json.loads(response.data)
        summary = data['summary']

        # Check device utilization
        utilization = summary['device_utilization']
        assert isinstance(utilization, dict)
        assert 'dev1' in utilization
        assert 0.0 <= utilization['dev1'] <= 1.0

    def test_summary_operation_stats(self, client, simple_request_data):
        """Test that summary contains operation statistics."""
        # Run simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id = json.loads(sim_response.data)['run_id']

        # Get summary
        response = client.get(f'/api/simulation/{run_id}/summary')
        data = json.loads(response.data)
        summary = data['summary']

        # Check operation stats
        op_stats = summary['operation_stats']
        assert isinstance(op_stats, dict)
        assert 'op1' in op_stats

        op1_stats = op_stats['op1']
        assert 'mean_duration' in op1_stats
        assert 'sample_count' in op1_stats
        assert op1_stats['sample_count'] == 1


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_workflow_single_sample(self, client, simple_request_data):
        """Test complete workflow from submission to result retrieval."""
        # 1. Submit simulation
        sim_response = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        assert sim_response.status_code == 200
        sim_data = json.loads(sim_response.data)
        run_id = sim_data['run_id']

        # 2. Retrieve events
        events_response = client.get(f'/api/simulation/{run_id}/events')
        assert events_response.status_code == 200
        events_data = json.loads(events_response.data)
        assert len(events_data['events']) > 0

        # 3. Retrieve summary
        summary_response = client.get(f'/api/simulation/{run_id}/summary')
        assert summary_response.status_code == 200
        summary_data = json.loads(summary_response.data)
        assert summary_data['summary']['num_samples_completed'] == 1

    def test_multiple_simulations_independent(self, client, simple_request_data, batch_request_data):
        """Test that multiple simulations are stored independently."""
        # Run first simulation
        response1 = client.post(
            '/api/simulate',
            data=json.dumps(simple_request_data),
            content_type='application/json'
        )
        run_id1 = json.loads(response1.data)['run_id']

        # Run second simulation
        response2 = client.post(
            '/api/simulate',
            data=json.dumps(batch_request_data),
            content_type='application/json'
        )
        run_id2 = json.loads(response2.data)['run_id']

        # Run IDs should be different
        assert run_id1 != run_id2

        # Both should be retrievable
        summary1 = client.get(f'/api/simulation/{run_id1}/summary')
        summary2 = client.get(f'/api/simulation/{run_id2}/summary')

        assert summary1.status_code == 200
        assert summary2.status_code == 200

        data1 = json.loads(summary1.data)
        data2 = json.loads(summary2.data)

        # Different sample counts
        assert data1['summary']['num_samples_completed'] == 1
        assert data2['summary']['num_samples_completed'] == 3
