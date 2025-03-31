# PagerDuty MCP Tools
The MCP server tools below expose PagerDuty API functionality to LLMs. These tools are designed to be used programmatically, with structured inputs and outputs.

## User Context
The MCP server tools use a user context to filter resources based on the current user's permissions. The user context contains:
- `user_id` (str): The current user's PagerDuty ID
- `team_ids` (List[str]): List of team IDs the user belongs to
- `service_ids` (List[str]): List of service IDs the user has access to
- `escalation_policy_ids` (List[str]): List of escalation policy IDs the user is part of

Many tools accept a `current_user_context` parameter (defaults to `True`) which automatically filters results based on this context. When `current_user_context` is `True`, you cannot use `user_ids`, `team_ids`, or `service_ids` parameters as they would conflict with the automatic filtering.

## Response Format
All API responses follow a consistent format:
```json
{
  "metadata": {
    "count": <count>,
    "description": "<A short summary of the results>"
  },
  <resource_type>: [ // Always pluralized for consistency, even if only one result is returned
    {
      ...
    },
    ...
  ],
  "error": {  // Only present if there's an error
    "message": "<error description>",
    "code": "<error code>"
  }
}
```

Note that `show_` methods still return lists in the format above, even though there will only be 1 list element, to ensure consistent response structure across queries.

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
- The `limit` parameter can be used to restrict the number of results returned by list operations. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned by default.

## Escalation Policy Tools
Tools for interacting with PagerDuty Escalation Policies. An Escalation Policy determines what User or Schedule will be Notified and in what order. This will happen when an Incident is triggered. Escalation Policies can be used by one or more Services.

### list_escalation_policies
List existing escalation policies.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, filters escalation policies to those associated with the current user (via `user_id` and `team_ids`). Cannot be used with `user_ids` or `team_ids`. |
| **query** | `str` | No | Filter escalation policies by name (case-insensitive substring match). |
| **user_ids** | `List[str]` | No | Filter results to escalation policies that include any of the given user IDs. Cannot be used with `current_user_context`. |
| **team_ids** | `List[str]` | No | Filter results to escalation policies that belong to any of the given teams. Cannot be used with `current_user_context`. |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of escalation policies in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `escalation_policies` (List[Dict]): A list of parsed escalation policy objects.

Each escalation policy object contains:
- `id` (str): The unique identifier for the escalation policy.
- `summary` (str): Summary of the escalation policy.
- `name` (str): The name of the escalation policy.
- `escalation_rules` (List[Dict]): a list of escalation rules, each containing:
  - `id` (str): The unique identifier for the escalation rule.
  - `escalation_delay_in_minutes` (int): delay before running escalation rule
  - `targets` (List[Dict]): a list of escalation targets, each containing:
    - `id` (str): The unique identifier for the escalation target.
    - `summary` (str): Summary of the escalation policy.
- `services` (List[Dict]): a list of services using the escalation policy, each containing:
  - `id` (str): The unique identifier for the service.
  - `summary` (str): Summary of the service.
- `num_loops` (int): number of times the escalation policy will loop
- `teams` (List[Dict]): a list of teams using the escalation policy, each including:
  - `id` (str): The unique identifier for the team.
  - `summary` (str): Summary of the team.
- `description` (str): description of the escalation policy.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type escalation_policies"
    },
    "escalation_policies": [
        {
          "id": "POLICY-1",
          "summary": "Test Escalation Policy 1",
          "name": "Test Escalation Policy 1",
          "escalation_rules": [...],
          "services": [...],
          "num_loops": 3,
          "teams": [...],
          "description": "policy description"
        },
        {
          "id": "POLICY-2",
          "summary": "Test Escalation Policy 2",
          "name": "Test Escalation Policy 2",
          "escalation_rules": [...],
          "services": [...],
          "num_loops": 3,
          "teams": [...],
          "description": "policy description"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query escalation policies:

1. List escalation policies in the current PagerDuty account using default query parameters (filter by the current user's ID and team IDs). Use this query to answer questions like "show my team's current escalation policies".
```python
list_escalation_policies()
```

2. List escalation policies for a specific team ID. Use this query to answer questions like "show escalation policies for TEAM_123".
```python
list_escalation_policies(
  team_ids=["TEAM_123"]
)
```

3. List escalation policies for a specific user ID. Use this query to answer questions like "show escalation policies for USER_123".
```python
list_escalation_policies(
  user_ids=["USER_123"]
)
```

4. List escalation policies that match the input query. Use this query to answer questions like "show escalation policies whose name matches SEARCH_STRING".
```python
list_escalation_policies(
  query="SEARCH_STRING"
)
```

### show_escalation_policy
Get detailed information about a specific escalation policy.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **policy_id** | `str` | Yes | The ID of the escalation policy to show. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single escalation policy**. The response format is **identical to `list_` methods**, but always contains exactly **one** policy in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type escalation_policies"
    },
    "escalation_policies": [
        {
          "id": "POLICY-1",
          "type": "escalation_policy",
          "summary": "Test Escalation Policy 1",
          "name": "Test Escalation Policy 1",
          "escalation_rules": [...],
          "services": [...],
          "teams": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query escalation policies:

1. Show detailed information about the given escalation policy ID. Use this query to answer questions like "show me information about escalation policy POLICY_123".
```python
show_escalation_policy(
  policy_id="POLICY_123"
)
```

## Incidents Tools
Tools for interacting with PagerDuty incidents. An Incident represents a problem or an issue that needs to be addressed and resolved.
Incidents can be thought of as a problem or an issue within your Service that needs to be addressed and resolved, they are normalized and de-duplicated.
Incidents can be triggered, acknowledged, or resolved, and are assigned to a User based on the Service's Escalation Policy.
A triggered Incident prompts a Notification to be sent to the current On-Call User(s) as defined in the Escalation Policy used by the Service.
Incidents are triggered through the Events API or are created by Integrations.

### list_incidents
List existing incidents.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, filters incidents to those associated with the current user's teams and services. Cannot be used with `team_ids` or `service_ids`. |
| **service_ids** | `List[str]` | No | Filter incidents by specific service IDs. Cannot be used with `current_user_context`. |
| **team_ids** | `List[str]` | No | Filter incidents by specific team IDs. Cannot be used with `current_user_context`. |
| **statuses** | `List[str]` | No | Filter incidents by status. Valid values are: `triggered`, `acknowledged`, `resolved`. Defaults to `["triggered", "acknowledged", "resolved"]`. |
| **since** | `str` | No | Start of date range in ISO8601 format. Default is 1 month ago. Must be a valid ISO8601 timestamp. |
| **until** | `str` | No | End of date range in ISO8601 format. Default is now. Must be a valid ISO8601 timestamp. |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of incidents in the following format:
- `metadata` (Dict): Contains result count and a description of the query results, plus:
    - `status_counts` (Dict[str, int]): Dictionary mapping each status to its count
    - `autoresolve_count` (int): Number of incidents that were auto-resolved (status='resolved' and last_status_change_by.type='service_reference')
    - `no_data_count` (int): Number of incidents with titles starting with "No Data:"
- `incidents` (List[Dict]): A list of parsed incident objects.

Each incident object contains:
- `id` (str): The unique identifier for the incident.
- `summary` (str): Summary of the incident.
- `title` (str): The title of the incident.
- `status` (str): Current status of the incident.
- `urgency` (str): Current urgency level of the incident.
- `body` (Dict): The incident body containing details and type.
- `service` (Dict): The service this incident belongs to.
- `assignments` (List[Dict]): List of current assignments.
- `acknowledgments` (List[Dict]): List of acknowledgments.
- `last_status_change_at` (str): Timestamp of last status change.
- `created_at` (str): Timestamp of incident creation.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type incidents",
        "status_counts": {
            "triggered": 1,
            "acknowledged": 0,
            "resolved": 1
        },
        "autoresolve_count": 0,
        "no_data_count": 1
    },
    "incidents": [
        {
            "id": "INCIDENT-1",
            "summary": "Test Incident 1",
            "title": "Test Incident 1",
            "status": "triggered",
            "urgency": "high",
            "body": {...},
            "service": {...},
            "assignments": [...],
            "acknowledgments": [...],
            "last_status_change_at": "2024-03-14T12:00:00Z",
            "created_at": "2024-03-14T12:00:00Z"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query incidents:

1. List all incidents for the current user's teams (including resolved):
```python
list_incidents()  # Uses defaults: current_user_context=True, statuses=["triggered", "acknowledged", "resolved"]
```

2. Get all incidents (including resolved) from the last week:
```python
list_incidents(
    statuses=["triggered", "acknowledged", "resolved"],
    since="2025-02-26T00:00:00Z"
)
```

3. Get incidents for specific services:
```python
list_incidents(
    current_user_context=False,
    service_ids=["SERVICE_123"], # example PagerDuty service ID
    statuses=["triggered", "acknowledged"]
)
```

### show_incident
Get detailed information about a specific incident.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **incident_id** | `str` | Yes | The ID of the incident to show. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single incident**. The response format is **identical to `list_` methods**, but always contains exactly **one** incident in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type incidents"
    },
    "incidents": [
        {
            "id": "INCIDENT-1",
            "summary": "Test Incident 1",
            "title": "Test Incident 1",
            "status": "triggered",
            "urgency": "high",
            "body": {...},
            "service": {...},
            "assignments": [...],
            "acknowledgments": [...],
            "last_status_change_at": "2024-03-14T12:00:00Z",
            "created_at": "2024-03-14T12:00:00Z"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for a specific incident:

1. Show detailed information about the given incident ID:
```python
show_incident(
  incident_id="INCIDENT_123"
)
```

### list_past_incidents
List incidents from the past 6 months that are similar to the input incident, ordered by similarity score.

The returned incidents are in a slimmed down format containing only id, created_at, self, and title.
Each incident also includes a similarity_score indicating how similar it is to the input incident.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **incident_id** | `str` | Yes | The ID or number of the incident to find similar incidents for |
| **limit** | `int` | No | The maximum number of past incidents to return. This parameter is passed directly to the PagerDuty API. Default in the API is 5. |
| **total** | `bool` | No | Whether to return the total number of incidents that match the criteria. This parameter is passed directly to the PagerDuty API. Default is False. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of similar incidents in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `incidents` (List[Dict]): A list of similar incident objects, each containing:
  - `id` (str): The incident ID
  - `created_at` (str): Creation timestamp
  - `self` (str): API URL for the incident
  - `title` (str): The incident title
  - `similarity_score` (float): Decimal value indicating similarity to the input incident

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 results for resource type incidents"
    },
    "incidents": [
        {
            "id": "Q1QKZKKE2FC88M",
            "created_at": "2025-02-08T19:34:42Z",
            "self": "https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M",
            "title": "Test Incident 1",
            "similarity_score": 190.21751
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for similar incidents:

1. Find similar incidents to a given incident:
```python
list_past_incidents(
    incident_id="INCIDENT_123"
)
```

2. Find similar incidents with a custom limit:
```python
list_past_incidents(
    incident_id="INCIDENT_123",
    limit=10
)
```

## On-Call Tools
Tools for interacting with PagerDuty On-Calls. An On-Call represents a contiguous unit of time for which a User will be On-Call for a given Escalation Policy and Escalation Rule.
This may be the result of that User always being On-Call for the Escalation Rule, or a block of time during which the computed result of a Schedule on that Escalation Rule puts the User On-Call.
During an On-Call, the User is expected to bear responsibility for responding to any Notifications they receives and working to resolve the associated Incident(s).
On-Calls cannot be created directly through the API; they are the computed result of how Escalation Policies and Schedules are configured. The API provides read-only access to the On-Calls generated by PagerDuty.

### list_oncalls
List existing on-call entries.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, filters on-calls to those associated with the current user. Cannot be used with `user_ids`. |
| **schedule_ids** | `List[str]` | No | Filter on-calls by specific schedule IDs. |
| **user_ids** | `List[str]` | No | Filter on-calls by specific user IDs. Cannot be used with `current_user_context`. |
| **escalation_policy_ids** | `List[str]` | No | Filter on-calls by specific escalation policy IDs. |
| **since** | `str` | No | Start of date range in ISO8601 format. Default is 1 month ago. |
| **until** | `str` | No | End of date range in ISO8601 format. Default is now. |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of on-call entries in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `oncalls` (List[Dict]): A list of parsed on-call objects.

Each on-call object contains:
- `id` (str): The unique identifier for the on-call entry.
- `summary` (str): Summary of the on-call entry.
- `start` (str): Start time of the on-call period.
- `end` (str): End time of the on-call period.
- `user` (Dict): The user who is on-call.
- `escalation_policy` (Dict): The escalation policy this on-call is for.
- `escalation_level` (int): The escalation level for this on-call.
- `schedule` (Dict): The schedule that generated this on-call (if applicable).

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type oncalls"
    },
    "oncalls": [
        {
            "id": "ONCALL-1",
            "summary": "Test On-Call 1",
            "start": "2024-03-14T00:00:00Z",
            "end": "2024-03-15T00:00:00Z",
            "user": {...},
            "escalation_policy": {...},
            "escalation_level": 1,
            "schedule": {...}
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query on-calls:

1. List current on-call entries (filtering by current user's user_id):
```python
list_oncalls()
```

2. List all on-calls for a specific schedule during a specified time frame:
```python
list_oncalls(
    schedule_ids=['SCHEDULE_123'],  # Example PagerDuty schedule ID
    since="2025-02-27T20:48:23.358605Z",
    until="2025-03-13T20:48:23.358561Z"
)
```

3. List on-calls for a specific escalation policy:
```python
list_oncalls(
    escalation_policy_ids=['ESCALATION_POLICY_123']  # Example PagerDuty escalation policy ID
)
```

## Schedule Tools
Tools for interacting with PagerDuty schedules. A Schedule determines the time periods that Users are On-Call.
Only On-Call Users are eligible to receive Notifications from Incidents.
The details of the On-Call Schedule specify which single User is On-Call for that Schedule at any given point in time.
An On-Call Schedule consists of one or more Schedule Layers that rotate a group of Users through the same shift at a set interval.
Schedules are used by Escalation Policies as an escalation target for a given Escalation Rule.

### list_schedules
List existing schedules.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **query** | `str` | No | Filter schedules whose names contain the search query (case-insensitive substring match). |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of schedules in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `schedules` (List[Dict]): A list of parsed schedule objects.

Each schedule object contains:
- `id` (str): The unique identifier for the schedule.
- `summary` (str): Summary of the schedule.
- `name` (str): The name of the schedule.
- `description` (str): Description of the schedule.
- `time_zone` (str): The time zone for the schedule.
- `schedule_layers` (List[Dict]): List of schedule layers.
- `teams` (List[Dict]): List of teams this schedule is assigned to.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type schedules"
    },
    "schedules": [
        {
            "id": "SCHEDULE-1",
            "summary": "Test Schedule 1",
            "name": "Test Schedule 1",
            "description": "Test schedule description",
            "time_zone": "UTC",
            "schedule_layers": [...],
            "teams": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query schedules:

1. List all schedules in the current PagerDuty account:
```python
list_schedules()
```

2. List schedules whose names match the input query:
```python
list_schedules(
  query="Schedule Name"
)
```

### show_schedule
Get detailed information about a specific schedule.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **schedule_id** | `str` | Yes | The ID of the schedule to show. |
| **since** | `str` | No | Start of date range in ISO8601 format. |
| **until** | `str` | No | End of date range in ISO8601 format. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single schedule**. The response format is **identical to `list_` methods**, but always contains exactly **one** schedule in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type schedules"
    },
    "schedules": [
        {
            "id": "SCHEDULE-1",
            "summary": "Test Schedule 1",
            "name": "Test Schedule 1",
            "description": "Test schedule description",
            "time_zone": "UTC",
            "schedule_layers": [...],
            "teams": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for a specific schedule:

1. Get detailed information about the given schedule ID:
```python
show_schedule(
    schedule_id="SCHEDULE_123"  # Example PagerDuty schedule ID
)
```

2. Get detailed information about who is on-call for the schedule during a specific time range:
```python
show_schedule(
    schedule_id="SCHEDULE_123",
    since="2025-02-27T20:48:23.358605Z",
    until="2025-03-13T20:48:23.358561Z"
)
```

## Service Tools
Tools for interacting with PagerDuty Services. A Service represents an entity you monitor (such as a web Service, email Service, or database Service.)
It is a container for related Incidents that associates them with Escalation Policies.
A Service is the focal point for Incident management; Services specify the configuration for the behavior of Incidents triggered on them.

### list_services
List existing services.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, filters services to those associated with the current user's teams. Cannot be used with `team_ids`. |
| **team_ids** | `List[str]` | No | Filter services by specific team IDs. Cannot be used with `current_user_context`. |
| **query** | `str` | No | Filter services whose names contain the search query (case-insensitive substring match). |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of services in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `services` (List[Dict]): A list of parsed service objects.

Each service object contains:
- `id` (str): The unique identifier for the service.
- `summary` (str): Summary of the service.
- `name` (str): The name of the service.
- `description` (str): Description of the service.
- `escalation_policy` (Dict): The escalation policy for this service.
- `teams` (List[Dict]): List of teams this service belongs to.
- `alert_creation` (str): When alerts are created for this service.
- `incident_urgency_rule` (Dict): Rules for incident urgency.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type services"
    },
    "services": [
        {
            "id": "SERVICE-1",
            "summary": "Test Service 1",
            "name": "Test Service 1",
            "description": "Test service description",
            "escalation_policy": {...},
            "teams": [...],
            "alert_creation": "create_incidents",
            "incident_urgency_rule": {...}
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query services:

1. List all services in the current PagerDuty account (filtering by current user's team IDs):
```python
list_services()
```

2. List services associated with specific teams:
```python
list_services(
    current_user_context=False,
    team_ids=['TEAM_123']  # Example PagerDuty team ID
)
```

### show_service
Get detailed information about a specific service.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **service_id** | `str` | Yes | The ID of the service to show. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single service**. The response format is **identical to `list_` methods**, but always contains exactly **one** service in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type services"
    },
    "services": [
        {
            "id": "SERVICE-1",
            "summary": "Test Service 1",
            "name": "Test Service 1",
            "description": "Test service description",
            "escalation_policy": {...},
            "teams": [...],
            "alert_creation": "create_incidents",
            "incident_urgency_rule": {...}
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for a specific service:

1. Show detailed information about the given service ID:
```python
show_service(
  service_id="SERVICE_123"
)
```

## Team Tools
Tools for interacting with PagerDuty teams. A Team is a collection of Users and Escalation Policies that may be associated with one or more Services.
Teams are used to group related Users and Escalation Policies together, making it easier to manage permissions and access control.

### list_teams
List existing teams.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **query** | `str` | No | Filter teams whose names contain the search query (case-insensitive substring match). |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of teams in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `teams` (List[Dict]): A list of parsed team objects.

Each team object contains:
- `id` (str): The unique identifier for the team.
- `summary` (str): Summary of the team.
- `name` (str): The name of the team.
- `description` (str): Description of the team.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type teams"
    },
    "teams": [
        {
            "id": "TEAM-1",
            "summary": "Test Team 1",
            "name": "Test Team 1",
            "description": "Test team description"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query teams:

1. List all teams in the current PagerDuty account:
```python
list_teams()
```

2. List teams whose names match the input query:
```python
list_teams(
    query="Team Name"
)
```

### show_team
Get detailed information about a specific team.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **team_id** | `str` | Yes | The ID of the team to show. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single team**. The response format is **identical to `list_` methods**, but always contains exactly **one** team in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type teams"
    },
    "teams": [
        {
            "id": "TEAM-1",
            "summary": "Test Team 1",
            "name": "Test Team 1",
            "description": "Test team description"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for a specific team:

1. Show detailed information about the given team ID:
```python
show_team(
    team_id="TEAM_123"  # Example PagerDuty team ID
)
```

## User Tools
Tools for interacting with PagerDuty users. A User is a member of your PagerDuty account who may be assigned to one or more Teams and may be On-Call for one or more Services.
Users can be notified of Incidents through various contact methods and notification rules.

### show_current_user
Get the current user's PagerDuty profile.

#### Parameters
None

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single user**. The response format is **identical to `list_` methods**, but always contains exactly **one** user in the list.

Each user object contains:
- `id` (str): The unique identifier for the user.
- `summary` (str): Summary of the user.
- `name` (str): The user's full name.
- `email` (str): The user's email address.
- `role` (str): The user's role in PagerDuty.
- `description` (str): Description of the user.
- `job_title` (str): The user's job title.
- `teams` (List[Dict]): List of teams the user belongs to.
- `contact_methods` (List[Dict]): List of contact methods for notifications.
- `notification_rules` (List[Dict]): List of notification rules.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type users"
    },
    "users": [
        {
            "id": "USER-1",
            "summary": "John Doe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "description": "Software Engineer",
            "job_title": "Senior Software Engineer",
            "teams": [...],
            "contact_methods": [...],
            "notification_rules": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for the current user:

1. Show current user's profile:
```python
show_current_user()  # Returns the authenticated user's profile
```

### list_users
List existing users.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, filters users to those associated with the current user's teams. Cannot be used with `team_ids`. |
| **team_ids** | `List[str]` | No | Filter users by specific team IDs. Cannot be used with `current_user_context`. |
| **query** | `str` | No | Filter users whose names contain the search query (case-insensitive substring match). |
| **limit** | `int` | No | Limit the number of results returned. If not specified, up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results will be returned. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a list of users in the following format:
- `metadata` (Dict): Contains result count and a description of the query results.
- `users` (List[Dict]): A list of parsed user objects.

Each user object contains:
- `id` (str): The unique identifier for the user.
- `summary` (str): Summary of the user.
- `name` (str): The user's full name.
- `email` (str): The user's email address.
- `role` (str): The user's role in PagerDuty.
- `description` (str): Description of the user.
- `job_title` (str): The user's job title.
- `teams` (List[Dict]): List of teams the user belongs to.
- `contact_methods` (List[Dict]): List of contact methods for notifications.
- `notification_rules` (List[Dict]): List of notification rules.

#### Example Response
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type users"
    },
    "users": [
        {
            "id": "USER-1",
            "summary": "John Doe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "description": "Software Engineer",
            "job_title": "Senior Software Engineer",
            "teams": [...],
            "contact_methods": [...],
            "notification_rules": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query users:

1. List all users in the current PagerDuty account (filtering by current user's team IDs):
```python
list_users()
```

2. List users associated with specific teams:
```python
list_users(
    current_user_context=False,
    team_ids=["TEAM_123"]  # Example PagerDuty team ID
)
```

3. List users for a specific service:
```python
list_users(
    current_user_context=False,
    service_ids=["SERVICE_123"]  # Example PagerDuty service ID
)
```

### show_user
Get detailed information about a specific user.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **user_id** | `str` | Yes | The ID of the user to show. |

#### Returns
Dict[str, Any]: A dictionary containing metadata and a **list** with a **single user**. The response format is **identical to `list_` methods**, but always contains exactly **one** user in the list.

#### Example Response
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type users"
    },
    "users": [
        {
            "id": "USER-1",
            "summary": "John Doe",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "user",
            "description": "Software Engineer",
            "job_title": "Senior Software Engineer",
            "teams": [...],
            "contact_methods": [...],
            "notification_rules": [...]
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query for a specific user:

1. Show detailed information about the given user ID:
```python
show_user(
    user_id="USER_123"  # Example PagerDuty user ID
)
```
