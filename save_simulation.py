#!/usr/bin/env python3
"""Helper script to save simulation results to a JSON file for later upload.

Usage:
    python save_simulation.py <run_id> [output_file]

Example:
    python save_simulation.py sim_run_20251126_145121_9da46a results.json
"""
import sys
import json
import requests
from pathlib import Path


def save_simulation_results(run_id: str, output_file: str = None):
    """Download and save simulation results from the API.

    Args:
        run_id: The simulation run ID
        output_file: Output filename (defaults to {run_id}.json)
    """
    base_url = "http://localhost:5001/api"

    if output_file is None:
        output_file = f"{run_id}.json"

    print(f"Fetching simulation results for {run_id}...")

    try:
        # Get events
        events_response = requests.get(f"{base_url}/simulation/{run_id}/events?limit=100000")
        events_response.raise_for_status()
        events_data = events_response.json()

        # Get summary
        summary_response = requests.get(f"{base_url}/simulation/{run_id}/summary")
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        # Combine into single JSON structure
        results = {
            "run_id": run_id,
            "workflow": {},  # Would need to be fetched separately if needed
            "scenario": {},  # Would need to be fetched separately if needed
            "events": events_data['events'],
            "summary": summary_data['summary'],
            "execution_time": 0.0,  # Not available from API
            "timestamp": "",  # Not available from API
        }

        # Save to file
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"✓ Simulation results saved to: {output_path.absolute()}")
        print(f"\nYou can now upload this file through the web interface at:")
        print(f"  http://localhost:5001/")
        print(f"\nOr use curl:")
        print(f"  curl -X POST http://localhost:5001/api/upload-results -F 'file=@{output_file}'")

    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API server")
        print("  Make sure the server is running: python main.py")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"✗ Error: {e}")
        if e.response.status_code == 404:
            print(f"  Run ID '{run_id}' not found. Make sure the simulation was completed.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python save_simulation.py <run_id> [output_file]")
        print("\nExample:")
        print("  python save_simulation.py sim_run_20251126_145121_9da46a results.json")
        sys.exit(1)

    run_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    save_simulation_results(run_id, output_file)
