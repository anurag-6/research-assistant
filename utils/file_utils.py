"""Utility functions for file operations."""
import os
from datetime import datetime
from langgraph.graph import StateGraph

from config import settings


def save_graph_image(graph: StateGraph, filename: str = "main_builder_graph.png") -> None:
    """Save the graph visualization to a PNG file."""
    png_data = graph.get_graph(xray=1).draw_mermaid_png()
    with open(filename, "wb") as f:
        f.write(png_data)
    print(f"Graph saved to {filename}")


def save_report(report: str, output_dir: str = "outputs") -> None:
    """Save the report to outputs directory with timestamp."""
    if report:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"final_report_{timestamp}.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {output_path}")
    else:
        print("No report found to write.")

