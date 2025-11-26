"""Main Flask application entry point."""
import logging
from flask import Flask, render_template_string
from flask_cors import CORS

from api.routes import api_bp


def create_app():
    """Create and configure Flask application.

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    @app.route('/examples/<filename>')
    def serve_example(filename):
        """Serve example workflow files."""
        from flask import send_from_directory
        import os
        examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
        return send_from_directory(examples_dir, filename)

    @app.route('/')
    def index():
        """Root endpoint with HTML documentation."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Instrument Workflow Simulator</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2.5.0/cytoscape-dagre.min.js"></script>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }
                header {
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    margin-bottom: 30px;
                    text-align: center;
                }
                h1 {
                    color: #2c3e50;
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                .subtitle {
                    color: #7f8c8d;
                    font-size: 1.1rem;
                    margin-top: 10px;
                }
                .badge {
                    display: inline-block;
                    padding: 6px 12px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    margin-left: 10px;
                }
                .card-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .card {
                    background: white;
                    border-radius: 12px;
                    padding: 24px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                }
                .card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 8px 12px rgba(0,0,0,0.15);
                }
                .card-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 16px;
                }
                .card-icon {
                    width: 48px;
                    height: 48px;
                    margin-right: 16px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                .card-icon svg {
                    width: 28px;
                    height: 28px;
                    fill: white;
                }
                .card-title {
                    font-size: 1.3rem;
                    color: #2c3e50;
                    font-weight: 600;
                }
                .card-content {
                    color: #5a6c7d;
                    line-height: 1.6;
                    font-size: 0.95rem;
                }
                .endpoint-card {
                    background: #f8f9fa;
                    padding: 12px 16px;
                    border-radius: 8px;
                    margin: 8px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                    border-left: 4px solid #667eea;
                }
                .method-badge {
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 0.8rem;
                    margin-right: 8px;
                }
                .method-post { background: #e74c3c; color: white; }
                .method-get { background: #27ae60; color: white; }
                code {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                }
                .code-block {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 16px;
                    border-radius: 8px;
                    overflow-x: auto;
                    margin: 12px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 0.85rem;
                    line-height: 1.5;
                }
                .feature-list {
                    list-style: none;
                    padding: 0;
                }
                .feature-list li {
                    padding: 8px 0;
                    display: flex;
                    align-items: center;
                }
                .feature-list li::before {
                    content: '✓';
                    color: #27ae60;
                    font-weight: bold;
                    margin-right: 12px;
                    font-size: 1.2rem;
                }
                @media (max-width: 768px) {
                    h1 { font-size: 1.8rem; }
                    .card-grid { grid-template-columns: 1fr; }
                }
                @media (max-width: 900px) {
                    .card-content > div[style*="grid-template-columns"] {
                        grid-template-columns: 1fr !important;
                    }
                }
                #workflowGraph {
                    width: 100%;
                    height: 500px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background: #fafafa;
                }
                .graph-legend {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-top: 12px;
                    padding: 12px;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 0.9rem;
                }
                .legend-color {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 2px solid #333;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Instrument Workflow Simulator</h1>
                    <span class="badge">v1.0.0-phase1a+viz</span>
                    <p class="subtitle">Discrete-event simulation engine for diagnostic and clinical chemistry instrument workflows</p>
                </header>

                <div class="card-grid">
                    <!-- Run Simulation Card - Full Width -->
                    <div class="card" style="grid-column: 1 / -1;">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M320-200v-560l440 280-440 280Zm80-280Zm0 134 210-134-210-134v268Z"/></svg>
                            </div>
                            <h2 class="card-title">Run Simulation</h2>
                        </div>
                        <div class="card-content">
                            <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-bottom: 20px;">
                                <!-- Left: Controls -->
                                <div>
                                    <p style="margin-bottom: 12px;"><strong>Load workflow file:</strong></p>
                                    <input type="file" id="workflowInput" accept=".json" style="display: none;">
                                    <button type="button" onclick="document.getElementById('workflowInput').click()" style="
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        border: none;
                                        padding: 12px 24px;
                                        border-radius: 8px;
                                        cursor: pointer;
                                        font-weight: 600;
                                        width: 100%;
                                        margin-bottom: 12px;
                                    ">Choose Workflow File</button>

                                    <div style="margin-bottom: 16px;">
                                        <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 8px;">Or load example:</p>
                                        <select id="exampleSelect" style="
                                            width: 100%;
                                            padding: 10px;
                                            border: 2px solid #e0e0e0;
                                            border-radius: 6px;
                                            font-size: 0.95rem;
                                            margin-bottom: 12px;
                                        ">
                                            <option value="">-- Select Example --</option>
                                            <option value="single_sample_pcr">Single Sample PCR</option>
                                            <option value="synchronized_batch_analyzer">Batch Analyzer (3 samples)</option>
                                            <option value="dna_extraction_liquid_handler">DNA Extraction (8 samples)</option>
                                        </select>
                                    </div>

                                    <div id="workflowFileName" style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 16px; min-height: 20px;"></div>

                                    <button id="runSimBtn" onclick="runSimulation()" disabled style="
                                        background: #27ae60;
                                        color: white;
                                        border: none;
                                        padding: 14px 28px;
                                        border-radius: 8px;
                                        cursor: pointer;
                                        font-weight: 600;
                                        width: 100%;
                                        font-size: 1.1rem;
                                        margin-bottom: 12px;
                                    ">▶ Run Simulation</button>

                                    <div id="simStatus" style="margin-top: 16px;"></div>
                                </div>

                                <!-- Right: JSON Editor -->
                                <div>
                                    <p style="margin-bottom: 8px;"><strong>Workflow & Scenario JSON:</strong></p>
                                    <textarea id="jsonEditor" style="
                                        width: 100%;
                                        height: 400px;
                                        font-family: 'Courier New', monospace;
                                        font-size: 0.85rem;
                                        padding: 12px;
                                        border: 2px solid #e0e0e0;
                                        border-radius: 8px;
                                        resize: vertical;
                                        background: #f8f9fa;
                                    " placeholder="Load a workflow file or select an example..."></textarea>
                                </div>
                            </div>

                            <script>
                                let currentWorkflowData = null;

                                // Handle workflow file upload
                                document.getElementById('workflowInput').addEventListener('change', async (e) => {
                                    const file = e.target.files[0];
                                    if (!file) return;

                                    document.getElementById('workflowFileName').textContent = `Loaded: ${file.name}`;

                                    const reader = new FileReader();
                                    reader.onload = (event) => {
                                        try {
                                            currentWorkflowData = JSON.parse(event.target.result);
                                            document.getElementById('jsonEditor').value = JSON.stringify(currentWorkflowData, null, 2);
                                            document.getElementById('runSimBtn').disabled = false;
                                            // Render workflow graph
                                            renderWorkflowGraph(currentWorkflowData);
                                        } catch (error) {
                                            document.getElementById('simStatus').innerHTML =
                                                `<p style="color: #e74c3c;">Error parsing JSON: ${error.message}</p>`;
                                        }
                                    };
                                    reader.readAsText(file);
                                });

                                // Handle example selection
                                document.getElementById('exampleSelect').addEventListener('change', async (e) => {
                                    const example = e.target.value;
                                    if (!example) return;

                                    document.getElementById('simStatus').innerHTML = '<p style="color: #3498db;">Loading example...</p>';

                                    try {
                                        const response = await fetch(`/examples/${example}.json`);
                                        if (!response.ok) throw new Error('Failed to load example');

                                        currentWorkflowData = await response.json();
                                        document.getElementById('jsonEditor').value = JSON.stringify(currentWorkflowData, null, 2);
                                        document.getElementById('workflowFileName').textContent = `Loaded: ${example}.json`;
                                        document.getElementById('runSimBtn').disabled = false;
                                        document.getElementById('simStatus').innerHTML = '';
                                        // Render workflow graph
                                        renderWorkflowGraph(currentWorkflowData);
                                    } catch (error) {
                                        document.getElementById('simStatus').innerHTML =
                                            `<p style="color: #e74c3c;">Error loading example: ${error.message}</p>`;
                                    }
                                });

                                // Run simulation
                                async function runSimulation() {
                                    const statusDiv = document.getElementById('simStatus');
                                    const runBtn = document.getElementById('runSimBtn');

                                    // Update JSON from editor in case user edited it
                                    try {
                                        currentWorkflowData = JSON.parse(document.getElementById('jsonEditor').value);
                                    } catch (error) {
                                        statusDiv.innerHTML = `<p style="color: #e74c3c;">Invalid JSON: ${error.message}</p>`;
                                        return;
                                    }

                                    runBtn.disabled = true;
                                    statusDiv.innerHTML = '<p style="color: #3498db; font-weight: bold;">🔄 Running simulation...</p>';

                                    try {
                                        const response = await fetch('/api/simulate', {
                                            method: 'POST',
                                            headers: { 'Content-Type': 'application/json' },
                                            body: JSON.stringify(currentWorkflowData)
                                        });

                                        const data = await response.json();

                                        if (response.ok) {
                                            statusDiv.innerHTML = `
                                                <p style="color: #27ae60; font-weight: bold;">✓ Simulation complete!</p>
                                                <p style="margin-top: 8px;">Run ID: <code>${data.run_id}</code></p>
                                                <p style="margin-top: 4px;">Events: ${data.event_count} | Samples: ${data.summary.num_samples_completed}</p>
                                                <p style="margin-top: 4px; color: #7f8c8d;">Opening dashboard...</p>
                                            `;

                                            // Auto-open dashboard after 1 second
                                            setTimeout(() => {
                                                window.open(`/api/simulation/${data.run_id}/visualize/dashboard`, '_blank');
                                                statusDiv.innerHTML += `
                                                    <p style="margin-top: 12px;">
                                                        <a href="/api/simulation/${data.run_id}/visualize/dashboard"
                                                           target="_blank"
                                                           style="
                                                               display: inline-block;
                                                               padding: 10px 20px;
                                                               background: #27ae60;
                                                               color: white;
                                                               text-decoration: none;
                                                               border-radius: 6px;
                                                               font-weight: 600;
                                                           ">View Dashboard Again</a>
                                                    </p>
                                                `;
                                            }, 1000);
                                        } else {
                                            statusDiv.innerHTML = `
                                                <p style="color: #e74c3c; font-weight: bold;">✗ Simulation failed</p>
                                                <p style="margin-top: 8px; color: #e74c3c;">${data.error_message || 'Unknown error'}</p>
                                                ${data.errors ? `<ul style="margin-top: 8px; color: #e74c3c;">${data.errors.map(e => `<li>${e}</li>`).join('')}</ul>` : ''}
                                            `;
                                        }
                                    } catch (error) {
                                        statusDiv.innerHTML = `<p style="color: #e74c3c;">Request failed: ${error.message}</p>`;
                                    } finally {
                                        runBtn.disabled = false;
                                    }
                                }
                            </script>
                        </div>
                    </div>

                    <!-- Workflow Graph Card - Full Width -->
                    <div class="card" style="grid-column: 1 / -1;">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M240-160q-50 0-85-35t-35-85q0-50 35-85t85-35q14 0 26.5 3t24.5 9l138-138q-6-12-9-24.5t-3-26.5q0-14 3-26.5t9-24.5L291-767q-12 6-24.5 9t-26.5 3q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 14-3 26.5t-9 24.5l138 138q12-6 24.5-9t26.5-3q14 0 26.5 3t24.5 9l138-138q-6-12-9-24.5t-3-26.5q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35q-14 0-26.5-3t-24.5-9L631-567q6 12 9 24.5t3 26.5q0 14-3 26.5t-9 24.5l138 138q12-6 24.5-9t26.5-3q50 0 85 35t35 85q0 50-35 85t-85 35q-50 0-85-35t-35-85q0-14 3-26.5t9-24.5L569-429q-12 6-24.5 9t-26.5 3q-14 0-26.5-3t-24.5-9L329-291q6 12 9 24.5t3 26.5q0 50-35 85t-85 35Zm0-80q17 0 28.5-11.5T280-280q0-17-11.5-28.5T240-320q-17 0-28.5 11.5T200-280q0 17 11.5 28.5T240-240Zm480 0q17 0 28.5-11.5T760-280q0-17-11.5-28.5T720-320q-17 0-28.5 11.5T680-280q0 17 11.5 28.5T720-240ZM240-720q17 0 28.5-11.5T280-760q0-17-11.5-28.5T240-800q-17 0-28.5 11.5T200-760q0 17 11.5 28.5T240-720Zm280 240q17 0 28.5-11.5T560-520q0-17-11.5-28.5T520-560q-17 0-28.5 11.5T480-520q0 17 11.5 28.5T520-480Zm0-40Zm-40 240Zm240 0ZM480-760Z"/></svg>
                            </div>
                            <h2 class="card-title">Workflow Graph</h2>
                        </div>
                        <div class="card-content">
                            <div id="graphPlaceholder" style="text-align: center; padding: 100px 20px; color: #7f8c8d;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 -960 960 960" style="fill: #bdc3c7; margin-bottom: 20px;"><path d="M240-160q-50 0-85-35t-35-85q0-50 35-85t85-35q14 0 26.5 3t24.5 9l138-138q-6-12-9-24.5t-3-26.5q0-14 3-26.5t9-24.5L291-767q-12 6-24.5 9t-26.5 3q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 14-3 26.5t-9 24.5l138 138q12-6 24.5-9t26.5-3q14 0 26.5 3t24.5 9l138-138q-6-12-9-24.5t-3-26.5q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35q-14 0-26.5-3t-24.5-9L631-567q6 12 9 24.5t3 26.5q0 14-3 26.5t-9 24.5l138 138q12-6 24.5-9t26.5-3q50 0 85 35t35 85q0 50-35 85t-85 35q-50 0-85-35t-35-85q0-14 3-26.5t9-24.5L569-429q-12 6-24.5 9t-26.5 3q-14 0-26.5-3t-24.5-9L329-291q6 12 9 24.5t3 26.5q0 50-35 85t-85 35Z"/></svg>
                                <p style="font-size: 1.1rem; font-weight: 500;">Load a workflow to see the graph</p>
                                <p style="font-size: 0.9rem; margin-top: 8px;">The workflow graph shows operations and their dependencies</p>
                            </div>
                            <div id="workflowGraph" style="display: none;"></div>
                            <div id="graphLegend" class="graph-legend" style="display: none;"></div>
                        </div>
                    </div>

                    <!-- Core API Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M440-280h80v-160h160v-80H520v-160h-80v160H280v80h160v160Zm40 200q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>
                            </div>
                            <h2 class="card-title">Core API</h2>
                        </div>
                        <div class="card-content">
                            <div class="endpoint-card">
                                <span class="method-badge method-post">POST</span>
                                <strong>/api/simulate</strong><br>
                                Execute simulation
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/api/simulation/{run_id}/events</strong><br>
                                Retrieve event log
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/api/simulation/{run_id}/summary</strong><br>
                                Get summary statistics
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/api/health</strong><br>
                                Health check
                            </div>
                        </div>
                    </div>

                    <!-- Visualization Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M160-160v-640h80v640h-80Zm160 0v-440h80v440h-80Zm160 0v-280h80v280h-80Zm160 0v-640h80v640h-80Zm160 0v-160h80v160h-80Z"/></svg>
                            </div>
                            <h2 class="card-title">Visualizations</h2>
                        </div>
                        <div class="card-content">
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/visualize/dashboard</strong><br>
                                Comprehensive dashboard
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/visualize/gantt</strong><br>
                                Device operations timeline
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/visualize/utilization</strong><br>
                                Device utilization chart
                            </div>
                            <div class="endpoint-card">
                                <span class="method-badge method-get">GET</span>
                                <strong>/visualize/queue</strong><br>
                                Queue length timeline
                            </div>
                        </div>
                    </div>

                    <!-- Features Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="m438-240 226-226-58-58-169 169-84-84-57 57 142 142Zm42 160q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg>
                            </div>
                            <h2 class="card-title">Features</h2>
                        </div>
                        <div class="card-content">
                            <ul class="feature-list">
                                <li>Discrete-event simulation using SimPy</li>
                                <li>Resource contention modeling</li>
                                <li>Three timing distributions</li>
                                <li>Interactive Plotly visualizations</li>
                                <li>Device utilization analytics</li>
                                <li>Bottleneck identification</li>
                                <li>Event filtering & pagination</li>
                                <li>94% test coverage</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Example Workflows Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M320-240h320v-80H320v80Zm0-160h320v-80H320v80ZM240-80q-33 0-56.5-23.5T160-160v-640q0-33 23.5-56.5T240-880h320l240 240v480q0 33-23.5 56.5T720-80H240Zm280-520v-200H240v640h480v-440H520ZM240-800v200-200 640-640Z"/></svg>
                            </div>
                            <h2 class="card-title">Examples</h2>
                        </div>
                        <div class="card-content">
                            <p><strong>single_sample_pcr.json</strong></p>
                            <p style="margin-bottom: 16px;">Simple PCR workflow with 1 sample, 2 devices, 3 operations</p>

                            <p><strong>synchronized_batch_analyzer.json</strong></p>
                            <p>Chemistry analyzer batch with 3 samples, 3 devices, 6 operations</p>
                        </div>
                    </div>

                    <!-- Load Results Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M440-320v-326L336-542l-56-58 200-200 200 200-56 58-104-104v326h-80ZM240-160q-33 0-56.5-23.5T160-240v-120h80v120h480v-120h80v120q0 33-23.5 56.5T720-160H240Z"/></svg>
                            </div>
                            <h2 class="card-title">Load Results</h2>
                        </div>
                        <div class="card-content">
                            <p style="margin-bottom: 16px;">Upload a simulation results JSON file to view visualizations:</p>
                            <form id="uploadForm" enctype="multipart/form-data" style="margin-bottom: 16px;">
                                <input type="file" id="fileInput" accept=".json" style="display: none;">
                                <button type="button" onclick="document.getElementById('fileInput').click()" style="
                                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                    color: white;
                                    border: none;
                                    padding: 12px 24px;
                                    border-radius: 8px;
                                    cursor: pointer;
                                    font-weight: 600;
                                    width: 100%;
                                    font-size: 1rem;
                                ">Choose File</button>
                            </form>
                            <div id="fileName" style="color: #7f8c8d; font-size: 0.9rem; margin-bottom: 12px;"></div>
                            <div id="uploadStatus"></div>
                            <script>
                                const fileInput = document.getElementById('fileInput');
                                const fileName = document.getElementById('fileName');
                                const uploadStatus = document.getElementById('uploadStatus');

                                fileInput.addEventListener('change', async (e) => {
                                    const file = e.target.files[0];
                                    if (!file) return;

                                    fileName.textContent = `Selected: ${file.name}`;
                                    uploadStatus.innerHTML = '<p style="color: #3498db;">Uploading...</p>';

                                    const formData = new FormData();
                                    formData.append('file', file);

                                    try {
                                        const response = await fetch('/api/upload-results', {
                                            method: 'POST',
                                            body: formData
                                        });

                                        const data = await response.json();

                                        if (response.ok) {
                                            uploadStatus.innerHTML = `
                                                <p style="color: #27ae60; font-weight: bold;">✓ Upload successful!</p>
                                                <p style="margin-top: 8px;">Run ID: <code>${data.run_id}</code></p>
                                                <a href="/api/simulation/${data.run_id}/visualize/dashboard"
                                                   target="_blank"
                                                   style="
                                                       display: inline-block;
                                                       margin-top: 12px;
                                                       padding: 10px 20px;
                                                       background: #27ae60;
                                                       color: white;
                                                       text-decoration: none;
                                                       border-radius: 6px;
                                                       font-weight: 600;
                                                   ">View Dashboard</a>
                                            `;
                                        } else {
                                            uploadStatus.innerHTML = `<p style="color: #e74c3c;">Error: ${data.error_message}</p>`;
                                        }
                                    } catch (error) {
                                        uploadStatus.innerHTML = `<p style="color: #e74c3c;">Upload failed: ${error.message}</p>`;
                                    }
                                });
                            </script>
                        </div>
                    </div>

                    <!-- Documentation Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M240-400h480v-80H240v80Zm0-120h480v-80H240v80Zm0-120h480v-80H240v80ZM80-80v-720q0-33 23.5-56.5T160-880h640q33 0 56.5 23.5T880-800v480q0 33-23.5 56.5T800-240H240L80-80Zm126-240h594v-480H160v525l46-45Zm-46 0v-480 480Z"/></svg>
                            </div>
                            <h2 class="card-title">Documentation</h2>
                        </div>
                        <div class="card-content">
                            <p>Comprehensive documentation available in the project repository:</p>
                            <div class="code-block">https://github.com/pdelmenico/instrument-workflow-sim</div>
                            <p style="margin-top: 12px;">See <code>README.md</code> for detailed usage instructions, API reference, and examples.</p>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                // Workflow graph visualization
                let cy = null;
                const deviceColors = {};
                const colorPalette = [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#43e97b', '#fa709a', '#fee140', '#30cfd0',
                    '#a8edea', '#fed6e3', '#c471ed', '#12c2e9'
                ];
                let colorIndex = 0;

                function getDeviceColor(deviceId) {
                    if (!deviceColors[deviceId]) {
                        deviceColors[deviceId] = colorPalette[colorIndex % colorPalette.length];
                        colorIndex++;
                    }
                    return deviceColors[deviceId];
                }

                function parseWorkflowToCytoscape(workflowData) {
                    if (!workflowData.workflow || !workflowData.workflow.operations) {
                        return { elements: [], devices: {} };
                    }

                    const workflow = workflowData.workflow;
                    const elements = [];
                    const devices = {};

                    // Create a map of operations
                    const operationMap = {};
                    workflow.operations.forEach(op => {
                        operationMap[op.operation_id] = op;
                        if (!devices[op.device_id]) {
                            devices[op.device_id] = workflow.devices.find(d => d.device_id === op.device_id);
                        }
                    });

                    // Create nodes for each operation
                    workflow.operations.forEach(op => {
                        let timingStr = '';
                        if (op.timing.type === 'fixed') {
                            timingStr = `Fixed: ${op.timing.value}s`;
                        } else if (op.timing.type === 'triangular') {
                            timingStr = `Tri: ${op.timing.min}-${op.timing.max}s`;
                        } else if (op.timing.type === 'exponential') {
                            timingStr = `Exp: μ=${op.timing.mean}s`;
                        }

                        elements.push({
                            data: {
                                id: op.operation_id,
                                label: op.operation_name || op.operation_id,
                                device: op.device_id,
                                timing: timingStr,
                                opType: op.operation_type || 'processing'
                            }
                        });
                    });

                    // Create edges based on base_sequence predecessors
                    if (workflow.base_sequence) {
                        workflow.base_sequence.forEach(step => {
                            if (step.predecessors && step.predecessors.length > 0) {
                                step.predecessors.forEach(predId => {
                                    elements.push({
                                        data: {
                                            id: `${predId}-${step.operation_id}`,
                                            source: predId,
                                            target: step.operation_id
                                        }
                                    });
                                });
                            }
                        });
                    }

                    return { elements, devices };
                }

                function renderWorkflowGraph(workflowData) {
                    const { elements, devices } = parseWorkflowToCytoscape(workflowData);

                    if (elements.length === 0) {
                        document.getElementById('graphPlaceholder').style.display = 'block';
                        document.getElementById('workflowGraph').style.display = 'none';
                        document.getElementById('graphLegend').style.display = 'none';
                        return;
                    }

                    // Hide placeholder, show graph
                    document.getElementById('graphPlaceholder').style.display = 'none';
                    document.getElementById('workflowGraph').style.display = 'block';
                    document.getElementById('graphLegend').style.display = 'flex';

                    // Reset color assignments
                    Object.keys(deviceColors).forEach(key => delete deviceColors[key]);
                    colorIndex = 0;

                    // Initialize cytoscape
                    if (cy) {
                        cy.destroy();
                    }

                    cy = cytoscape({
                        container: document.getElementById('workflowGraph'),
                        elements: elements,
                        style: [
                            {
                                selector: 'node',
                                style: {
                                    'label': 'data(label)',
                                    'text-valign': 'center',
                                    'text-halign': 'center',
                                    'background-color': function(ele) {
                                        return getDeviceColor(ele.data('device'));
                                    },
                                    'shape': 'roundrectangle',
                                    'width': '180',
                                    'height': '80',
                                    'border-width': 3,
                                    'border-color': '#333',
                                    'color': '#fff',
                                    'font-size': '14px',
                                    'font-weight': 'bold',
                                    'text-wrap': 'wrap',
                                    'text-max-width': '160px'
                                }
                            },
                            {
                                selector: 'edge',
                                style: {
                                    'width': 3,
                                    'line-color': '#95a5a6',
                                    'target-arrow-color': '#95a5a6',
                                    'target-arrow-shape': 'triangle',
                                    'curve-style': 'bezier',
                                    'arrow-scale': 1.5
                                }
                            }
                        ],
                        layout: {
                            name: 'dagre',
                            rankDir: 'LR',
                            nodeSep: 50,
                            rankSep: 80,
                            padding: 30
                        }
                    });

                    // Add tooltips
                    cy.on('mouseover', 'node', function(evt) {
                        const node = evt.target;
                        const data = node.data();
                        node.style({
                            'border-width': 5,
                            'border-color': '#000'
                        });

                        // Could add a proper tooltip here
                        console.log(`${data.label}\nDevice: ${data.device}\nTiming: ${data.timing}\nType: ${data.opType}`);
                    });

                    cy.on('mouseout', 'node', function(evt) {
                        evt.target.style({
                            'border-width': 3,
                            'border-color': '#333'
                        });
                    });

                    // Build legend
                    const legendDiv = document.getElementById('graphLegend');
                    legendDiv.innerHTML = '<strong style="width: 100%; margin-bottom: 4px;">Devices:</strong>';

                    Object.entries(devices).forEach(([deviceId, device]) => {
                        const color = getDeviceColor(deviceId);
                        const item = document.createElement('div');
                        item.className = 'legend-item';
                        item.innerHTML = `
                            <div class="legend-color" style="background-color: ${color};"></div>
                            <span><strong>${device.device_name || deviceId}</strong> (capacity: ${device.resource_capacity})</span>
                        `;
                        legendDiv.appendChild(item);
                    });
                }
            </script>
        </body>
        </html>
        """
        return render_template_string(html)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
