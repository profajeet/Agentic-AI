# Agentic Orchestrator

A master agent system built with LangGraph that orchestrates multiple specialized agents for handling different types of tasks. The system includes a database agent and a service agent, both integrated with MCP servers.

## Features

- Master agent for orchestrating specialized agents
- Database agent for handling database operations
- Service agent for handling API and service operations
- MCP server integration for both database and service agents
- Intelligent routing based on message content
- Extensible architecture for adding new agents

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MCP_DATABASE_SERVER_URL=your_database_mcp_server_url
   MCP_SERVICE_SERVER_URL=your_service_mcp_server_url
   ```

## Usage

```python
from AI_Controller import MasterAgent

# Initialize the master agent
master_agent = MasterAgent()

# Process messages
response = master_agent.process_message("Query the database for user information")
print(response)
```

## Architecture

The system uses LangGraph to create a workflow that routes messages to appropriate agents based on their content:

1. **Master Agent**: Coordinates between specialized agents and handles general queries
2. **Database Agent**: Handles database-related operations and queries
3. **Service Agent**: Manages service operations and API calls

Each agent is integrated with its respective MCP server for enhanced functionality.

## Adding New Agents

To add a new agent:

1. Create a new agent class following the pattern of existing agents
2. Add the agent to the MasterAgent class
3. Update the router function in `_create_workflow()` to handle the new agent's domain
4. Add the new agent's node and edges to the workflow

## License

MIT 