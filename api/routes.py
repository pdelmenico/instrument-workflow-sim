"""Flask REST API routes for simulation service."""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from dataclasses import asdict

from flask import Blueprint, request, jsonify

from src.simulation.core import SimulationEngine
from src.simulation.validators import WorkflowValidator, ScenarioValidator
from src.simulation.models import SimulationEvent, SimulationSummary
from src.simulation.visualization import (
    create_gantt_chart,
    create_utilization_chart,
    create_queue_timeline,
    create_sample_journey_chart,
    create_operation_stats_chart,
    create_dashboard
)


logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# In-memory storage for simulation results (Phase 1a)
# In production, this would be a database
simulation_results: Dict[str, Dict[str, Any]] = {}


@api_bp.route('/simulate', methods=['POST'])
def simulate():
    """Execute a simulation with provided workflow and scenario.

    Request Body:
        {
            "workflow": {...},  # Workflow definition
            "scenario": {...}   # Scenario configuration
        }

    Returns:
        200 OK: Simulation completed successfully
        {
            "status": "success",
            "run_id": "sim_run_...",
            "execution_time_sec": 0.123,
            "event_count": 15,
            "summary": {...}
        }

        400 Bad Request: Validation error
        {
            "status": "validation_error",
            "errors": [...],
            "warnings": [...]
        }

        500 Internal Server Error: Simulation execution error
        {
            "status": "simulation_error",
            "error_message": "..."
        }
    """
    try:
        # Parse request JSON
        data = request.get_json(force=True, silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "error_message": "No JSON data provided"
            }), 400

        workflow = data.get('workflow')
        scenario = data.get('scenario')

        if not workflow or not scenario:
            return jsonify({
                "status": "error",
                "error_message": "Both 'workflow' and 'scenario' must be provided"
            }), 400

        # Validate workflow
        workflow_validator = WorkflowValidator()
        workflow_result = workflow_validator.validate(workflow)

        if not workflow_result.is_valid:
            return jsonify({
                "status": "validation_error",
                "errors": workflow_result.errors,
                "warnings": workflow_result.warnings
            }), 400

        # Validate scenario
        scenario_validator = ScenarioValidator()
        scenario_result = scenario_validator.validate(scenario, workflow)

        if not scenario_result.is_valid:
            return jsonify({
                "status": "validation_error",
                "errors": scenario_result.errors,
                "warnings": scenario_result.warnings
            }), 400

        # Generate unique run ID
        run_id = f"sim_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Execute simulation
        start_time = datetime.now()

        logger.info(f"Starting simulation {run_id}")
        engine = SimulationEngine(workflow, scenario)
        events, summary = engine.run()

        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        logger.info(f"Simulation {run_id} completed in {execution_time:.3f}s")

        # Store results
        simulation_results[run_id] = {
            "run_id": run_id,
            "workflow": workflow,
            "scenario": scenario,
            "events": events,
            "summary": summary,
            "execution_time": execution_time,
            "timestamp": start_time.isoformat()
        }

        # Prepare summary for JSON serialization
        summary_dict = asdict(summary)

        # Convert dataclass fields in summary_dict
        for device_id, queue_stats in summary_dict['device_queue_stats'].items():
            if hasattr(queue_stats, '__dict__'):
                summary_dict['device_queue_stats'][device_id] = asdict(queue_stats)

        for op_id, op_stats in summary_dict['operation_stats'].items():
            if hasattr(op_stats, '__dict__'):
                summary_dict['operation_stats'][op_id] = asdict(op_stats)

        for op_id, wait_stats in summary_dict['operation_wait_times'].items():
            if hasattr(wait_stats, '__dict__'):
                summary_dict['operation_wait_times'][op_id] = asdict(wait_stats)

        return jsonify({
            "status": "success",
            "run_id": run_id,
            "execution_time_sec": execution_time,
            "event_count": len(events),
            "summary": summary_dict
        }), 200

    except Exception as e:
        logger.error(f"Simulation error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "simulation_error",
            "error_message": str(e)
        }), 500


@api_bp.route('/simulation/<run_id>/events', methods=['GET'])
def get_events(run_id: str):
    """Retrieve event log from a completed simulation.

    Path Parameters:
        run_id: Simulation run identifier

    Query Parameters:
        sample_id: Filter by sample ID (optional)
        operation_id: Filter by operation ID (optional)
        device_id: Filter by device ID (optional)
        event_type: Filter by event type (optional)
        limit: Maximum number of events to return (default: 1000)
        offset: Pagination offset (default: 0)

    Returns:
        200 OK: Events retrieved successfully
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    events = result['events']

    # Apply filters
    sample_id = request.args.get('sample_id')
    operation_id = request.args.get('operation_id')
    device_id = request.args.get('device_id')
    event_type = request.args.get('event_type')

    filtered_events = events

    if sample_id:
        filtered_events = [e for e in filtered_events if e.sample_id == sample_id]

    if operation_id:
        filtered_events = [e for e in filtered_events if e.operation_id == operation_id]

    if device_id:
        filtered_events = [e for e in filtered_events if e.device_id == device_id]

    if event_type:
        filtered_events = [e for e in filtered_events if e.event_type == event_type]

    # Apply pagination
    limit = int(request.args.get('limit', 1000))
    offset = int(request.args.get('offset', 0))

    paginated_events = filtered_events[offset:offset + limit]

    # Convert events to dict
    events_dict = [asdict(e) for e in paginated_events]

    return jsonify({
        "status": "success",
        "run_id": run_id,
        "filter_applied": {
            "sample_id": sample_id,
            "operation_id": operation_id,
            "device_id": device_id,
            "event_type": event_type
        },
        "event_count": len(paginated_events),
        "total_events": len(filtered_events),
        "events": events_dict
    }), 200


@api_bp.route('/simulation/<run_id>/summary', methods=['GET'])
def get_summary(run_id: str):
    """Retrieve summary statistics from a completed simulation.

    Path Parameters:
        run_id: Simulation run identifier

    Returns:
        200 OK: Summary retrieved successfully
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    summary = result['summary']

    # Convert summary to dict
    summary_dict = asdict(summary)

    # Convert nested dataclasses
    for device_id, queue_stats in summary_dict['device_queue_stats'].items():
        if hasattr(queue_stats, '__dict__'):
            summary_dict['device_queue_stats'][device_id] = asdict(queue_stats)

    for op_id, op_stats in summary_dict['operation_stats'].items():
        if hasattr(op_stats, '__dict__'):
            summary_dict['operation_stats'][op_id] = asdict(op_stats)

    for op_id, wait_stats in summary_dict['operation_wait_times'].items():
        if hasattr(wait_stats, '__dict__'):
            summary_dict['operation_wait_times'][op_id] = asdict(wait_stats)

    return jsonify({
        "status": "success",
        "run_id": run_id,
        "summary": summary_dict
    }), 200


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.

    Returns:
        200 OK: Service is healthy
    """
    return jsonify({
        "status": "healthy",
        "service": "instrument-workflow-simulator",
        "version": "1.0.0-phase1a"
    }), 200


@api_bp.route('/simulation/<run_id>/visualize/gantt', methods=['GET'])
def visualize_gantt(run_id: str):
    """Generate Gantt chart visualization for a simulation run.

    Path Parameters:
        run_id: Simulation run identifier

    Returns:
        200 OK: HTML with interactive Gantt chart
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    events = result['events']

    fig = create_gantt_chart(events, title=f"Device Operations - {run_id}")

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/simulation/<run_id>/visualize/utilization', methods=['GET'])
def visualize_utilization(run_id: str):
    """Generate device utilization bar chart for a simulation run.

    Path Parameters:
        run_id: Simulation run identifier

    Returns:
        200 OK: HTML with interactive utilization chart
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    summary = result['summary']

    fig = create_utilization_chart(summary, title=f"Device Utilization - {run_id}")

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/simulation/<run_id>/visualize/queue', methods=['GET'])
def visualize_queue(run_id: str):
    """Generate queue length timeline for a simulation run.

    Path Parameters:
        run_id: Simulation run identifier

    Query Parameters:
        device_id: Filter by specific device (optional)

    Returns:
        200 OK: HTML with interactive queue timeline
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    events = result['events']
    device_id = request.args.get('device_id')

    fig = create_queue_timeline(
        events,
        device_id=device_id,
        title=f"Queue Length Over Time - {run_id}"
    )

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/simulation/<run_id>/visualize/sample', methods=['GET'])
def visualize_sample(run_id: str):
    """Generate sample journey visualization for a simulation run.

    Path Parameters:
        run_id: Simulation run identifier

    Query Parameters:
        sample_id: Filter by specific sample (optional)

    Returns:
        200 OK: HTML with interactive sample journey chart
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    events = result['events']
    sample_id = request.args.get('sample_id')

    fig = create_sample_journey_chart(
        events,
        sample_id=sample_id,
        title=f"Sample Journey - {run_id}"
    )

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/simulation/<run_id>/visualize/operations', methods=['GET'])
def visualize_operations(run_id: str):
    """Generate operation statistics chart for a simulation run.

    Path Parameters:
        run_id: Simulation run identifier

    Returns:
        200 OK: HTML with interactive operation stats chart
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    summary = result['summary']

    fig = create_operation_stats_chart(summary, title=f"Operation Statistics - {run_id}")

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/simulation/<run_id>/visualize/dashboard', methods=['GET'])
def visualize_dashboard(run_id: str):
    """Generate comprehensive dashboard with all visualizations.

    Path Parameters:
        run_id: Simulation run identifier

    Returns:
        200 OK: HTML with interactive dashboard
        404 Not Found: Run ID does not exist
    """
    if run_id not in simulation_results:
        return jsonify({
            "status": "error",
            "error_message": f"Simulation run '{run_id}' not found"
        }), 404

    result = simulation_results[run_id]
    events = result['events']
    summary = result['summary']

    fig = create_dashboard(events, summary, title=f"Simulation Dashboard - {run_id}")

    return fig.to_html(full_html=True, include_plotlyjs='cdn')


@api_bp.route('/upload-results', methods=['POST'])
def upload_results():
    """Upload simulation results JSON file for visualization.

    Request:
        Form data with file upload (key: 'file')

    Returns:
        200 OK: File uploaded and processed successfully
        {
            "status": "success",
            "run_id": "uploaded_...",
            "message": "Results loaded successfully"
        }

        400 Bad Request: Invalid file or format
        {
            "status": "error",
            "error_message": "..."
        }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "error_message": "No file provided"
            }), 400

        file = request.files['file']

        # Check if filename is present
        if file.filename == '':
            return jsonify({
                "status": "error",
                "error_message": "No file selected"
            }), 400

        # Check file extension
        if not file.filename.endswith('.json'):
            return jsonify({
                "status": "error",
                "error_message": "File must be a JSON file"
            }), 400

        # Read and parse JSON
        import json
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            return jsonify({
                "status": "error",
                "error_message": f"Invalid JSON format: {str(e)}"
            }), 400

        # Generate unique run ID for uploaded file
        run_id = f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        # Validate structure - check for required fields
        required_fields = ['workflow', 'scenario', 'events', 'summary']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "status": "error",
                "error_message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Convert events from dict to SimulationEvent objects
        events = []
        for event_dict in data['events']:
            events.append(SimulationEvent(**event_dict))

        # Convert summary from dict to SimulationSummary object
        # Need to handle nested dataclasses
        from src.simulation.models import DeviceQueueStats, OperationStats, OperationWaitStats

        summary_dict = data['summary']

        # Convert nested dataclasses
        device_queue_stats = {}
        for device_id, stats_dict in summary_dict['device_queue_stats'].items():
            device_queue_stats[device_id] = DeviceQueueStats(**stats_dict)

        operation_stats = {}
        for op_id, stats_dict in summary_dict['operation_stats'].items():
            operation_stats[op_id] = OperationStats(**stats_dict)

        operation_wait_times = {}
        for op_id, stats_dict in summary_dict['operation_wait_times'].items():
            operation_wait_times[op_id] = OperationWaitStats(**stats_dict)

        summary = SimulationSummary(
            total_simulation_time=summary_dict['total_simulation_time'],
            num_samples_completed=summary_dict['num_samples_completed'],
            num_samples_failed=summary_dict['num_samples_failed'],
            device_utilization=summary_dict['device_utilization'],
            device_queue_stats=device_queue_stats,
            operation_stats=operation_stats,
            operation_wait_times=operation_wait_times,
            total_throughput=summary_dict['total_throughput'],
            mean_sample_cycle_time=summary_dict['mean_sample_cycle_time'],
            min_sample_cycle_time=summary_dict['min_sample_cycle_time'],
            max_sample_cycle_time=summary_dict['max_sample_cycle_time'],
            bottleneck_device=summary_dict['bottleneck_device'],
            bottleneck_utilization=summary_dict['bottleneck_utilization'],
            bottleneck_queue_delay=summary_dict.get('bottleneck_queue_delay', 0.0)
        )

        # Store in simulation_results
        simulation_results[run_id] = {
            "run_id": run_id,
            "workflow": data['workflow'],
            "scenario": data['scenario'],
            "events": events,
            "summary": summary,
            "execution_time": data.get('execution_time', 0.0),
            "timestamp": data.get('timestamp', datetime.now().isoformat())
        }

        logger.info(f"Uploaded simulation results stored as {run_id}")

        return jsonify({
            "status": "success",
            "run_id": run_id,
            "message": "Results loaded successfully",
            "event_count": len(events),
            "samples_completed": summary.num_samples_completed
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error_message": f"Failed to process file: {str(e)}"
        }), 500
