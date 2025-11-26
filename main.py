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
                    <!-- Quick Start Card -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="M440-200h80v-40h40q17 0 28.5-11.5T600-280v-120q0-17-11.5-28.5T560-440H440v-40h160v-80h-80v-40h-80v40h-40q-17 0-28.5 11.5T360-520v120q0 17 11.5 28.5T400-360h120v40H360v80h80v40ZM240-80q-33 0-56.5-23.5T160-160v-640q0-33 23.5-56.5T240-880h320l240 240v480q0 33-23.5 56.5T720-80H240Zm280-560v-160H240v640h480v-480H520ZM240-800v160-160 640-640Z"/></svg>
                            </div>
                            <h2 class="card-title">Quick Start</h2>
                        </div>
                        <div class="card-content">
                            <p><strong>1. Run a simulation:</strong></p>
                            <div class="code-block">curl -X POST http://localhost:5001/api/simulate \\
  -H "Content-Type: application/json" \\
  -d @examples/single_sample_pcr.json</div>
                            <p><strong>2. Get the <code>run_id</code> from response</strong></p>
                            <p><strong>3. View visualizations:</strong></p>
                            <div class="code-block">http://localhost:5001/api/simulation/{run_id}/visualize/dashboard</div>
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
        </body>
        </html>
        """
        return render_template_string(html)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
