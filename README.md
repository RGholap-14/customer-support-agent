# customer-support-agent

A simple LangGraph-based customer support agent starter project.

## Structure

- `app.py` runs the workflow from the command line.
- `graph.py` defines the LangGraph workflow.
- `state.py` contains the shared state schema.
- `nodes.py` includes the router and response node.
- `tools.py` contains placeholder tools for future extension.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your OpenAI API key to `.env`.
3. Run the app:
   ```bash
   python app.py
   ```
