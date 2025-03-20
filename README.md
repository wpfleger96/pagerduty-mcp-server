# PagerDuty MCP Server
A server that exposes PagerDuty API functionality to LLMs. This server is designed to be used programmatically, with structured inputs and outputs.

## Overview
The PagerDuty MCP Server provides a set of tools for interacting with the PagerDuty API. These tools are designed to be used by LLMs to perform various operations on PagerDuty resources such as incidents, services, teams, and users.

## Features
- List and show incidents
- List and show services
- List and show teams
- List and show users
- List and show schedules
- List and show escalation policies
- List and show on-calls

## Response Format
All API responses follow a consistent format:
```json
{
  "metadata": {
    "count": <int>,  // Number of results
    "description": "<str>"  // A short summary of the results
  },
  <resource_type>: [ // Always pluralized for consistency, even if only one result is returned
    {
      ...
    },
    ...
  ],
  "error": {  // Only present if there's an error
    "message": "<str>",  // Human-readable error description
    "code": "<str>"  // Machine-readable error code
  }
}
```

### Error Handling
When an error occurs, the response will include an error object with the following structure:
```json
{
  "metadata": {
    "count": 0,
    "description": "Error occurred while processing request"
  },
  "error": {
    "message": "Invalid user ID provided",
    "code": "INVALID_USER_ID"
  }
}
```

Common error scenarios include:
- Invalid resource IDs (e.g., user_id, team_id, service_id)
- Missing required parameters
- Invalid parameter values
- API request failures
- Response processing errors

### Parameter Validation
- All ID parameters must be valid PagerDuty resource IDs
- Date parameters must be valid ISO8601 timestamps
- List parameters (e.g., `statuses`, `team_ids`) must contain valid values
- Invalid values in list parameters will be ignored
- Required parameters cannot be `None` or empty strings
- For `statuses` in `list_incidents`, only `triggered`, `acknowledged`, and `resolved` are valid values
- For `urgency` in incidents, only `high` and `low` are valid values

## Example Usage
Here's an example of how to use the PagerDuty MCP Server to list incidents:

```python
from pagerduty_mcp_server import list_incidents

# List all active incidents for the current user's teams
response = list_incidents()

# Get all incidents (including resolved) from the last week
response = list_incidents(
    statuses=["triggered", "acknowledged", "resolved"],
    since="2024-03-07T00:00:00Z"
)

# Get incidents for specific services
response = list_incidents(
    current_user_context=False,
    service_ids=["SERVICE_123"],  # Example PagerDuty service ID
    statuses=["triggered", "acknowledged"]
)
```

## Installation
```sh
# Clone the repository
git clone https://github.com/wpfleger96/pagerduty-mcp-server.git
cd pagerduty-mcp-server

# Install dependencies
brew install uv
uv sync
```

## Configuration
The PagerDuty MCP Server requires a PagerDuty API token to be set in the environment:
```bash
PAGERDUTY_API_TOKEN=your_api_token_here
```

## User Context
Many functions support automatic filtering based on the current user's context. When `current_user_context=True` (default), results are filtered to only show resources the current user has access to:
- Incidents for teams the user belongs to
- Services the user has access to
- Teams the user belongs to
- Escalation policies the user is part of

When using `current_user_context=True` (default), you cannot use `user_ids`, `team_ids`, or `service_ids` parameters as they would conflict with the automatic filtering.

## Usage
### As Goose Extension
```json
{
  "type": "stdio",
  "enabled": true,
  "args": [
    "run",
    "python",
    "-m",
    "pagerduty_mcp_server"
  ],
  "commandInput": "uv run python -m pagerduty_mcp_server",
  "timeout": 300,
  "id": "pagerduty-mcp-server",
  "name": "pagerduty-mcp-server",
  "description": "pagerduty-mcp-server",
  "env_keys": [
    "PAGERDUTY_API_KEY"
  ],
  "cmd": "uv"
}
```

### As Standalone Server
```sh
uv run python -m pagerduty_mcp_server
```

## Development
### Running Tests
Note that most tests require a real connection to PagerDuty API, so you'll need to set `PAGERDUTY_API_TOKEN` in the environment before running the full test suite.

```bash
uv run pytest
```

To run only unit tests (i.e. tests that don't require `PAGERDUTY_API_KEY` set in the environment):
```sh
uv run pytest -m unit
```

To run only integration tests:
```bash
uv run python -m integration
```

To run only tests related to a specific submodule:
```bash
uv run python -m <client|escalation_policies|...>
```

### Debug Server with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp_server
```

## Reference
### Project Structure
```
pagerduty-mcp-server/
├─ docs/                    # Documentation files
│  ├─ tools.md             # Detailed tool documentation
├─ src/                    # Source code
│  ├─ pagerduty_mcp_server/
│  │  ├─ parsers/         # Response parsing modules
│  │  │  ├─ escalation_policy_parser.py
│  │  │  ├─ incident_parser.py
│  │  │  ├─ oncall_parser.py
│  │  │  ├─ schedule_parser.py
│  │  │  ├─ service_parser.py
│  │  │  ├─ team_parser.py
│  │  │  ├─ user_parser.py
│  │  ├─ __init__.py
│  │  ├─ __main__.py      # Server entry point
│  │  ├─ client.py        # PagerDuty API client
│  │  ├─ escalation_policies.py
│  │  ├─ incident_processor.py
│  │  ├─ incidents.py
│  │  ├─ oncalls.py
│  │  ├─ schedules.py
│  │  ├─ server.py        # MCP server implementation
│  │  ├─ services.py
│  │  ├─ teams.py
│  │  ├─ users.py
│  │  ├─ utils.py         # Utility functions
├─ tests/                  # Test files
│  ├─ fixtures/           # Test fixtures
│  ├─ integration/        # Integration tests
│  ├─ unit/              # Unit tests
│  ├─ conftest.py        # Pytest configuration
├─ .gitignore
├─ pyproject.toml         # Project configuration
├─ uv.lock               # Dependency lock file
├─ README.md
```

### Documentation
[Tool Documentation](./docs/tools.md) - Detailed information about available tools including parameters, return types, and example queries

### Conventions
- All API responses follow the standard format with metadata, resource list, and optional error
- Resource names in responses are always pluralized for consistency
- All functions that return a single item still return a list with one element
- Error responses include both a message and a code
- All timestamps are in ISO8601 format
