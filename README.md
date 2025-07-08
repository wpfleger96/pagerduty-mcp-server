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

## Getting Started

1. Initialize your local Python environment:
```sh
cd pagerduty-mcp-server
brew install uv
uv sync
```
2. The PagerDuty MCP Server requires a PagerDuty API token. You can provide this in two ways:

   **Option 1: Environment Variable**
   ```bash
   export PAGERDUTY_API_TOKEN=your_api_token_here
   ```

   **Option 2: .env File (Recommended)**
   Create a `.env` file in the project root:
   ```bash
   echo "PAGERDUTY_API_TOKEN=your_api_token_here" > .env
   ```
   
   The server will automatically load environment variables from the `.env` file if present.

## Usage
### As Goose Extension
In Goose:
1. Go to **Settings > Extensions > Add**.
2. Set **Type** to **StandardIO**.
3. Enter the absolute path to this project's CLI in your environment, for example:
   ```bash
   uv run /path/to/mcp/pagerduty-mcp-server/.venv/bin/pagerduty-mcp-server
   ```
4. Enable the extension and confirm that Goose identifies your tools.

### As Standalone Server
```sh
uv run path/to/repo/pagerduty-mcp-server/.venv/bin/pagerduty-mcp-server
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
- If no limit is specified, the server will return up to {pagerduty-mcp-server.utils.RESPONSE_LIMIT} results by default

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
The test suite includes both unit tests and integration tests. Integration tests require a real connection to the PagerDuty API, while unit tests can run without API access.

The `pytest-cov` args are optional, use them to include a test coverage report in the output.

To run all tests (integration tests will be automatically skipped if `PAGERDUTY_API_TOKEN` is not set):
```bash
uv run pytest [--cov=src --cov-report=term-missing]
```

To run only unit tests (no API token required):
```bash
uv run pytest -m unit [--cov=src --cov-report=term-missing]
```

To run only integration tests (requires `PAGERDUTY_API_TOKEN` set in environment):
```bash
uv run pytest -m integration [--cov=src --cov-report=term-missing]
```

To run only parser tests:
```bash
uv run pytest -m parsers [--cov=src --cov-report=term-missing]
```

To run only tests related to a specific submodule:
```bash
uv run pytest -m <client|escalation_policies|...> [--cov=src --cov-report=term-missing]
```

### Debug Server with MCP Inspector
```bash
npx @modelcontextprotocol/inspector uv run path/to/repo/pagerduty-mcp-server/.venv/bin/pagerduty-mcp-server
```

### Documentation
[Tool Documentation](./docs/tools.md) - Detailed information about available tools including parameters, return types, and example queries

### Conventions
- All API responses follow the standard format with metadata, resource list, and optional error
- Resource names in responses are always pluralized for consistency
- All functions that return a single item still return a list with one element
- Error responses include both a message and a code
- All timestamps are in ISO8601 format
- Tests are marked with pytest markers to indicate their type (unit/integration), the resource they test (incidents, teams, etc.), and whether they test parsing functionality ("parsers" marker)


### Example Queries
- Are there any incidents assigned to me currently in pagerduty?
- Do I have any upcoming on call schedule in next 2 weeks?
- Who else is a member of the personalization team?