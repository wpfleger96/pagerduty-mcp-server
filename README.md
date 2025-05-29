# PagerDuty MCP Server
A server that exposes PagerDuty API functionality to LLMs. This server is designed to be used programmatically, with structured inputs and outputs.

<a href="https://glama.ai/mcp/servers/@wpfleger96/pagerduty-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@wpfleger96/pagerduty-mcp-server/badge" alt="PagerDuty Server MCP server" />
</a>

[![PyPI Downloads](https://img.shields.io/pypi/dm/pagerduty-mcp-server.svg)](https://pypi.org/project/pagerduty-mcp-server/)
[![Python Versions](https://img.shields.io/pypi/pyversions/pagerduty-mcp-server.svg)](https://pypi.org/project/pagerduty-mcp-server/)
[![GitHub Contributors](https://img.shields.io/github/contributors/wpfleger96/pagerduty-mcp-server.svg)](https://github.com/wpfleger96/pagerduty-mcp-server/graphs/contributors)
[![PyPI version](https://img.shields.io/pypi/v/pagerduty-mcp-server.svg)](https://pypi.org/project/pagerduty-mcp-server/)
[![License](https://img.shields.io/github/license/wpfleger96/pagerduty-mcp-server.svg)](https://github.com/wpfleger96/pagerduty-mcp-server/blob/main/LICENSE)

## Overview
The PagerDuty MCP Server provides a set of tools for interacting with the PagerDuty API. These tools are designed to be used by LLMs to perform various operations on PagerDuty resources such as incidents, services, teams, and users.

## Installation
### From PyPI
```bash
pip install pagerduty-mcp-server
```

### From Source
```sh
# Clone the repository
git clone https://github.com/wpfleger96/pagerduty-mcp-server.git
cd pagerduty-mcp-server

# Install dependencies
brew install uv
uv sync
```

## Requirements
- Python 3.13 or higher
- PagerDuty API key

## Configuration
The PagerDuty MCP Server requires a PagerDuty API key to be set in the environment:
```bash
PAGERDUTY_API_KEY=your_api_key_here
```

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

### Claude/Cursor
```json
{
  "mcpServers": {
    "pagerduty-mcp-server": {
      "command": "uvx",
      "args": [pagerduty-mcp-server"],
      "env": {
          "PAGERDUTY_API_KEY": __PAGERDUTY_API_KEY__
      }
    }
  }
}
```

### As Standalone Server
```sh
uv run python -m pagerduty_mcp_server
```

## Response Format
All API responses follow a consistent format:
```json
{
  "metadata": {
    "count": <int>,  // Number of results
    "description": "<str>"  // A short summary of the results
  },
  <resource_type>: [ // Always pluralized for consistency, even if one result is returned
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
- The `limit` parameter can be used to restrict the number of results returned by list operations

### Rate Limiting and Pagination
- The server respects PagerDuty's rate limits
- The server automatically handles pagination for you
- The `limit` parameter can be used to control the number of results returned by list operations
- If no limit is specified, the server will return up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results by default

### Example Usage
```python
from pagerduty_mcp_server import incidents
from pagerduty_mcp_server.utils import RESPONSE_LIMIT

# List all incidents (including resolved) for the current user's teams
incidents_list = incidents.list_incidents()

# List only active incidents
active_incidents = incidents.list_incidents(statuses=['triggered', 'acknowledged'])

# List incidents for specific services
service_incidents = incidents.list_incidents(service_ids=['SERVICE-1', 'SERVICE-2'])

# List incidents for specific teams
team_incidents = incidents.list_incidents(team_ids=['TEAM-1', 'TEAM-2'])

# List incidents within a date range
date_range_incidents = incidents.list_incidents(
    since='2024-03-01T00:00:00Z',
    until='2024-03-14T23:59:59Z'
)

# List incidents with a limit on the number of results
limited_incidents = incidents.list_incidents(limit=10)

# List incidents with the default limit
default_limit_incidents = incidents.list_incidents(limit=RESPONSE_LIMIT)
```

## User Context
Many functions accept a `current_user_context` parameter (defaults to `True`) which automatically filters results based on this context. When `current_user_context` is `True`, you cannot use certain filter parameters as they would conflict with the automatic filtering:

- For all resource types:
  - `user_ids` cannot be used with `current_user_context=True`
- For incidents:
  - `team_ids` and `service_ids` cannot be used with `current_user_context=True`
- For services:
  - `team_ids` cannot be used with `current_user_context=True`
- For escalation policies:
  - `team_ids` cannot be used with `current_user_context=True`
- For on-calls:
  - `user_ids` cannot be used with `current_user_context=True`
  - `schedule_ids` can still be used to filter by specific schedules
  - The query will show on-calls for all escalation policies associated with the current user's teams
  - This is useful for answering questions like "who is currently on-call for my team?"
  - The current user's ID is not used as a filter, so you'll see all team members who are on-call

## Development
### Running Tests
Note that most tests require a real connection to PagerDuty API, so you'll need to set `PAGERDUTY_API_KEY` in the environment before running the full test suite.

```bash
uv run pytest
```

To run only unit tests (i.e. tests that don't require `PAGERDUTY_API_KEY` set in the environment):
```bash
uv run pytest -m unit
```

To run only integration tests:
```bash
uv run pytest -m integration
```

To run only parser tests:
```bash
uv run pytest -m parsers
```

To run only tests related to a specific submodule:
```bash
uv run pytest -m <client|escalation_policies|...>
```

### Debug Server with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv run python -m pagerduty_mcp_server
```

## Contributions

### Releases
This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automated releases. Commit messages determine version bumps:
- `feat:` → minor version (1.0.0 → 1.1.0)
- `fix:` → patch version (1.0.0 → 1.0.1)
- `BREAKING CHANGE:` → major version (1.0.0 → 2.0.0)

The CHANGELOG.md, GitHub releases, and PyPI packages are updated automatically.

### Documentation
[Tool Documentation](./docs/tools.md) - Detailed information about available tools including parameters, return types, and example queries

### Conventions
- All API responses follow the standard format with metadata, resource list, and optional error
- Resource names in responses are always pluralized for consistency
- All functions that return a single item still return a list with one element
- Error responses include both a message and a code
- All timestamps are in ISO8601 format
- Tests are marked with pytest markers to indicate their type (unit/integration), the resource they test (incidents, teams, etc.), and whether they test parsing functionality ("parsers" marker)
