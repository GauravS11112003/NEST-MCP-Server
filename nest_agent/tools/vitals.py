import os
from google.adk.tools.agent_tool import ToolContext

def read_wearable_vitals(tool_context: ToolContext) -> str:
    """Reads the latest real-time wearable vitals for the mother and infant."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "DEMO_VITALS.md")
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading vitals: {e}"
