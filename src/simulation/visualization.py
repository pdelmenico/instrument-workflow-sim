"""Visualization functions for simulation results using Plotly."""
import logging
from typing import List, Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from src.simulation.models import SimulationEvent, SimulationSummary


logger = logging.getLogger(__name__)


def create_gantt_chart(events: List[SimulationEvent], title: str = "Device Operations Timeline") -> go.Figure:
    """Create a Gantt chart showing operations on each device over time.

    Each bar represents an operation execution, color-coded by sample.
    Shows device contention and idle time visually.

    Args:
        events: List of simulation events
        title: Chart title

    Returns:
        Plotly Figure object

    Example:
        >>> events, summary = engine.run()
        >>> fig = create_gantt_chart(events)
        >>> fig.show()
    """
    # Filter to START and COMPLETE events
    start_events = {(e.sample_id, e.operation_id): e
                   for e in events if e.event_type == "START"}
    complete_events = {(e.sample_id, e.operation_id): e
                      for e in events if e.event_type == "COMPLETE"}

    # Build gantt data
    gantt_data = []
    for key, start_event in start_events.items():
        if key in complete_events:
            complete_event = complete_events[key]
            gantt_data.append({
                'Task': start_event.device_id,
                'Start': start_event.timestamp,
                'Finish': complete_event.timestamp,
                'Resource': start_event.sample_id,
                'Operation': start_event.operation_id,
                'Duration': complete_event.duration,
                'WaitTime': start_event.wait_time
            })

    if not gantt_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(title="No operations to display")
        return fig

    df = pd.DataFrame(gantt_data)

    # Create figure using plotly express timeline
    fig = px.timeline(
        df,
        x_start='Start',
        x_end='Finish',
        y='Task',
        color='Resource',
        hover_data=['Operation', 'Duration', 'WaitTime'],
        title=title,
        labels={'Task': 'Device', 'Resource': 'Sample'}
    )

    # Update layout
    fig.update_yaxes(categoryorder='category ascending')
    fig.update_layout(
        xaxis_title="Simulation Time (seconds)",
        height=max(400, len(df['Task'].unique()) * 80),
        showlegend=True,
        hovermode='closest'
    )

    return fig


def create_utilization_chart(summary: SimulationSummary, title: str = "Device Utilization") -> go.Figure:
    """Create a bar chart showing device utilization percentages.

    Highlights the bottleneck device in red.

    Args:
        summary: SimulationSummary object
        title: Chart title

    Returns:
        Plotly Figure object
    """
    devices = list(summary.device_utilization.keys())
    utilizations = [summary.device_utilization[d] * 100 for d in devices]

    # Color bottleneck device red, others blue
    colors = ['red' if d == summary.bottleneck_device else 'steelblue'
              for d in devices]

    fig = go.Figure(data=[
        go.Bar(
            x=devices,
            y=utilizations,
            marker_color=colors,
            text=[f"{u:.1f}%" for u in utilizations],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<extra></extra>'
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title="Device",
        yaxis_title="Utilization (%)",
        yaxis_range=[0, min(105, max(utilizations) + 10)],
        height=400,
        showlegend=False
    )

    # Add reference line at 100%
    fig.add_hline(y=100, line_dash="dash", line_color="gray",
                  annotation_text="100% capacity", annotation_position="right")

    return fig


def create_queue_timeline(events: List[SimulationEvent],
                         device_id: str = None,
                         title: str = "Queue Length Over Time") -> go.Figure:
    """Create a line chart showing queue length over time for devices.

    Args:
        events: List of simulation events
        device_id: If specified, show only this device. Otherwise show all devices.
        title: Chart title

    Returns:
        Plotly Figure object
    """
    # Filter QUEUED events
    queued_events = [e for e in events if e.event_type == "QUEUED"]

    if device_id:
        queued_events = [e for e in queued_events if e.device_id == device_id]

    if not queued_events:
        fig = go.Figure()
        fig.update_layout(title="No queue data to display")
        return fig

    # Group by device
    devices = {}
    for event in queued_events:
        if event.device_id not in devices:
            devices[event.device_id] = {'timestamps': [], 'queue_lengths': []}
        devices[event.device_id]['timestamps'].append(event.timestamp)
        devices[event.device_id]['queue_lengths'].append(event.device_queue_length)

    # Create traces for each device
    fig = go.Figure()

    for dev_id, data in devices.items():
        fig.add_trace(go.Scatter(
            x=data['timestamps'],
            y=data['queue_lengths'],
            mode='lines+markers',
            name=dev_id,
            hovertemplate='<b>%{fullData.name}</b><br>Time: %{x:.2f}s<br>Queue Length: %{y}<extra></extra>'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Simulation Time (seconds)",
        yaxis_title="Queue Length",
        height=400,
        hovermode='x unified'
    )

    return fig


def create_sample_journey_chart(events: List[SimulationEvent],
                                sample_id: str = None,
                                title: str = "Sample Journey Through Workflow") -> go.Figure:
    """Create a timeline showing a sample's journey through operations.

    Shows QUEUED (waiting), START (processing begins), and COMPLETE (done) events.

    Args:
        events: List of simulation events
        sample_id: If specified, show only this sample. Otherwise show all samples.
        title: Chart title

    Returns:
        Plotly Figure object
    """
    if sample_id:
        filtered_events = [e for e in events if e.sample_id == sample_id]
    else:
        filtered_events = events

    if not filtered_events:
        fig = go.Figure()
        fig.update_layout(title="No sample data to display")
        return fig

    # Create dataframe for visualization
    data = []
    for event in filtered_events:
        data.append({
            'Sample': event.sample_id,
            'Timestamp': event.timestamp,
            'Event': event.event_type,
            'Operation': event.operation_id,
            'Device': event.device_id,
            'WaitTime': event.wait_time,
            'Duration': event.duration
        })

    df = pd.DataFrame(data)

    # Create scatter plot
    event_colors = {'QUEUED': 'orange', 'START': 'green', 'COMPLETE': 'blue'}

    fig = go.Figure()

    for sample in df['Sample'].unique():
        sample_df = df[df['Sample'] == sample]

        for event_type in ['QUEUED', 'START', 'COMPLETE']:
            event_df = sample_df[sample_df['Event'] == event_type]
            if not event_df.empty:
                fig.add_trace(go.Scatter(
                    x=event_df['Timestamp'],
                    y=event_df['Operation'],
                    mode='markers',
                    name=f"{sample} - {event_type}",
                    marker=dict(size=10, color=event_colors.get(event_type, 'gray')),
                    hovertemplate='<b>%{fullData.name}</b><br>Time: %{x:.2f}s<br>Operation: %{y}<extra></extra>'
                ))

    fig.update_layout(
        title=title,
        xaxis_title="Simulation Time (seconds)",
        yaxis_title="Operation",
        height=max(400, len(df['Operation'].unique()) * 60),
        hovermode='closest'
    )

    return fig


def create_operation_stats_chart(summary: SimulationSummary,
                                 title: str = "Operation Duration Statistics") -> go.Figure:
    """Create a box plot showing operation duration statistics.

    Shows mean, min, max, and standard deviation for each operation.

    Args:
        summary: SimulationSummary object
        title: Chart title

    Returns:
        Plotly Figure object
    """
    operations = []
    means = []
    mins = []
    maxs = []
    stdevs = []

    for op_id, stats in summary.operation_stats.items():
        if stats.sample_count > 0:
            operations.append(op_id)
            means.append(stats.mean_duration)
            mins.append(stats.min_duration)
            maxs.append(stats.max_duration)
            stdevs.append(stats.stdev_duration)

    if not operations:
        fig = go.Figure()
        fig.update_layout(title="No operation statistics to display")
        return fig

    fig = go.Figure()

    # Add error bars showing min/max range
    fig.add_trace(go.Bar(
        x=operations,
        y=means,
        error_y=dict(
            type='data',
            symmetric=False,
            array=[maxs[i] - means[i] for i in range(len(operations))],
            arrayminus=[means[i] - mins[i] for i in range(len(operations))]
        ),
        marker_color='steelblue',
        text=[f"{m:.1f}s" for m in means],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Mean: %{y:.2f}s<br>Stdev: %{customdata:.2f}s<extra></extra>',
        customdata=stdevs
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Operation",
        yaxis_title="Duration (seconds)",
        height=400,
        showlegend=False
    )

    return fig


def create_dashboard(events: List[SimulationEvent],
                    summary: SimulationSummary,
                    title: str = "Simulation Dashboard") -> go.Figure:
    """Create a comprehensive dashboard with multiple subplots.

    Combines Gantt chart, utilization, queue timeline, and stats in one figure.

    Args:
        events: List of simulation events
        summary: SimulationSummary object
        title: Dashboard title

    Returns:
        Plotly Figure object with subplots
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Device Operations Timeline", "Device Utilization",
                       "Queue Length Over Time", "Operation Durations"),
        specs=[[{"type": "scatter", "rowspan": 1, "colspan": 2}, None],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 1. Gantt chart (simplified as scatter for subplot)
    start_events = {(e.sample_id, e.operation_id): e
                   for e in events if e.event_type == "START"}
    complete_events = {(e.sample_id, e.operation_id): e
                      for e in events if e.event_type == "COMPLETE"}

    gantt_data = []
    for key, start_event in start_events.items():
        if key in complete_events:
            complete_event = complete_events[key]
            gantt_data.append({
                'device': start_event.device_id,
                'start': start_event.timestamp,
                'end': complete_event.timestamp,
                'sample': start_event.sample_id
            })

    if gantt_data:
        df_gantt = pd.DataFrame(gantt_data)
        for sample in df_gantt['sample'].unique():
            sample_df = df_gantt[df_gantt['sample'] == sample]
            for _, row in sample_df.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=[row['start'], row['end'], row['end'], row['start'], row['start']],
                        y=[row['device'], row['device'], row['device'], row['device'], row['device']],
                        fill='toself',
                        name=sample,
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=1, col=1
                )

    # 2. Device utilization
    devices = list(summary.device_utilization.keys())
    utilizations = [summary.device_utilization[d] * 100 for d in devices]
    colors = ['red' if d == summary.bottleneck_device else 'steelblue'
              for d in devices]

    fig.add_trace(
        go.Bar(x=devices, y=utilizations, marker_color=colors,
               showlegend=False, text=[f"{u:.1f}%" for u in utilizations]),
        row=2, col=1
    )

    # 3. Queue stats (as bar chart of max queue length)
    queue_devices = list(summary.device_queue_stats.keys())
    max_queues = [summary.device_queue_stats[d].max_queue_length
                  for d in queue_devices]

    fig.add_trace(
        go.Bar(x=queue_devices, y=max_queues, marker_color='orange',
               showlegend=False, text=max_queues),
        row=2, col=2
    )

    # Update layout
    fig.update_xaxes(title_text="Time (s)", row=1, col=1)
    fig.update_yaxes(title_text="Device", row=1, col=1)
    fig.update_xaxes(title_text="Device", row=2, col=1)
    fig.update_yaxes(title_text="Utilization (%)", row=2, col=1)
    fig.update_xaxes(title_text="Device", row=2, col=2)
    fig.update_yaxes(title_text="Max Queue Length", row=2, col=2)

    fig.update_layout(
        title_text=title,
        height=800,
        showlegend=False
    )

    return fig
