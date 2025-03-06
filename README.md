# PagerDuty MCP Server
A Model Context Protocol (MCP) server that enables communication with the PagerDuty platform.

## Features
- Supports list and get operations for the following PagerDuty models:
  - Escalation policies
  - Incidents
  - Oncalls
  - Services
  - Teams
  - Users
- See [Tool Documentation](docs/tools.md) for complete details

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
Set the following environment variables:
```sh
PAGERDUTY_API_KEY=your_api_key
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

### As Standalone Server
```sh
uv run python -m pagerduty_mcp_server
```

## Documentation
- [Tool Documentation](docs/tools.md) - Detailed information about available tools and how to use them