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
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #34495e;
                    margin-top: 30px;
                }
                .section {
                    background: white;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .endpoint {
                    margin: 10px 0;
                    padding: 12px;
                    background: #ecf0f1;
                    border-left: 4px solid #3498db;
                    border-radius: 4px;
                    font-family: monospace;
                }
                .method {
                    display: inline-block;
                    padding: 4px 8px;
                    background: #3498db;
                    color: white;
                    border-radius: 3px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .method.get { background: #27ae60; }
                .method.post { background: #e74c3c; }
                code {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }
                .example {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                    margin: 10px 0;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 8px;
                    background: #27ae60;
                    color: white;
                    border-radius: 12px;
                    font-size: 12px;
                    margin-left: 10px;
                }
            </style>
        </head>
        <body>
            <h1>🔬 Instrument Workflow Simulator <span class="badge">v1.0.0-phase1a+viz</span></h1>

            <div class="section">
                <p><strong>Discrete-event simulation engine for diagnostic and clinical chemistry instrument workflows.</strong></p>
                <p>Analyze device contention, identify bottlenecks, and optimize resource allocation with comprehensive visualizations.</p>
            </div>

            <div class="section">
                <h2>📊 Quick Start</h2>
                <p>1. Run a simulation with an example workflow:</p>
                <div class="example">curl -X POST http://localhost:5001/api/simulate \\
  -H "Content-Type: application/json" \\
  -d @examples/single_sample_pcr.json</div>

                <p>2. Get the <code>run_id</code> from the response.</p>

                <p>3. View visualizations by opening these URLs in your browser:</p>
                <div class="example">http://localhost:5001/api/simulation/{run_id}/visualize/dashboard</div>
            </div>

            <div class="section">
                <h2>🎯 Core API Endpoints</h2>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/api/simulate</strong> - Execute simulation with workflow and scenario
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/events</strong> - Retrieve event log (supports filtering)
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/summary</strong> - Get summary statistics
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/health</strong> - Health check endpoint
                </div>
            </div>

            <div class="section">
                <h2>📈 Visualization Endpoints (New!)</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/dashboard</strong> - Comprehensive dashboard with all charts
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/gantt</strong> - Device operations Gantt chart
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/utilization</strong> - Device utilization bar chart
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/queue</strong> - Queue length timeline
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/sample</strong> - Sample journey through workflow
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/simulation/{run_id}/visualize/operations</strong> - Operation duration statistics
                </div>
            </div>

            <div class="section">
                <h2>💡 Example Workflows</h2>
                <p>Two example workflows are available in the <code>examples/</code> directory:</p>
                <ul>
                    <li><strong>single_sample_pcr.json</strong> - Simple PCR workflow (1 sample, 2 devices, 3 operations)</li>
                    <li><strong>synchronized_batch_analyzer.json</strong> - Chemistry analyzer batch (3 samples, 3 devices, 6 operations)</li>
                </ul>
            </div>

            <div class="section">
                <h2>🔧 Features</h2>
                <ul>
                    <li>✅ Discrete-event simulation using SimPy</li>
                    <li>✅ Resource contention modeling with device queues</li>
                    <li>✅ Three timing distributions (fixed, triangular, exponential)</li>
                    <li>✅ Comprehensive statistics (utilization, bottlenecks, cycle times)</li>
                    <li>✅ Interactive Plotly visualizations</li>
                    <li>✅ Event filtering and pagination</li>
                    <li>✅ Deterministic simulations with random seed</li>
                    <li>✅ 165 tests with 94% code coverage</li>
                </ul>
            </div>

            <div class="section">
                <h2>📚 Documentation</h2>
                <p>For detailed documentation, see the <code>README.md</code> file in the project repository.</p>
                <p>GitHub: <code>https://github.com/pdelmenico/instrument-workflow-sim</code></p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
