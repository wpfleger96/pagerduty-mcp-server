# PagerDuty MCP Tools
The MCP server tools below expose PagerDuty API functionality to LLMs. These tools are designed to be used programmatically, with structured inputs and outputs.

## User Context
The MCP server tools use a user context to filter resources based on the current user's permissions. The user context contains:
- `user_id` (str): The current user's PagerDuty ID
- `team_ids` (List[str]): List of team IDs the user belongs to
- `service_ids` (List[str]): List of service IDs the user has access to
- `escalation_policy_ids` (List[str]): List of escalation policy IDs the user is part of

Many tools accept a `current_user_context` parameter (defaults to `True`) which automatically filters results based on this context. When `current_user_context` is `True`, you cannot use certain filter parameters as they would conflict with the automatic filtering:

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

## Query Filtering
- All list operations support a `limit` parameter to control the maximum number of results returned. If not specified, the API will return up to {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results by default.
- When querying for large datasets that exceed {pagerduty_mcp_server.utils.RESPONSE_LIMIT} results, you must split your query into smaller chunks based on relevant dimensions. For example, you could split by time (e.g., querying each week of a month separately) or by resource type (e.g., querying each team's incidents separately).

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
List the on-call entries during a given time range. An oncall-entry contains the user that is on-call for the given schedule, escalation policy, or time range and also includes the schedule and escalation policy that the user is on-call for.

The behavior of this function differs based on whether time parameters are provided:

1. Without time parameters (since/until):
   - Returns the current on-call assignments for the specified schedules/policies/users
   - Useful for answering questions like "who is currently on-call?"
   - Example: list_oncalls(schedule_ids=["SCHEDULE_123"]) returns current on-call for that schedule

2. With time parameters (since/until):
   - Returns all on-call assignments that overlap with the specified time range
   - May return multiple entries if the time range spans multiple on-call shifts
   - Useful for answering questions like "who will be on-call next week?"
   - Example: list_oncalls(schedule_ids=["SCHEDULE_123"], since="2024-03-20T00:00:00Z", until="2024-03-27T00:00:00Z")
     might return two entries if the schedule has weekly shifts

#### Escalation Levels
PagerDuty uses a hierarchical escalation system:
- Level 1: Primary on-call. This is the engineer who is currently on-call and will receive the initial incident notifications.
- Level 2: Backup on-call. If the primary (Level 1) doesn't acknowledge an incident within the configured delay period, it will be escalated to the backup on-call.
- Level 3: Final escalation path. This is typically used as a final backup if neither the primary nor backup respond to an incident.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| **current_user_context** | `bool` | No | If `True`, shows on-calls for all escalation policies associated with the current user's teams. Cannot be used with `user_ids`. (default: True) |
| **schedule_ids** | `List[str]` | No | Return only on-calls for the specified schedule IDs (optional, can be used with current_user_context) |
| **user_ids** | `List[str]` | No | Return only on-calls for the specified user IDs (optional, cannot be used with current_user_context) |
| **escalation_policy_ids** | `List[str]` | No | Return only on-calls for the specified escalation policy IDs (optional) |
| **since** | `str` | No | Start of date range in ISO8601 format (optional). Default is 1 month ago |
| **until** | `str` | No | End of date range in ISO8601 format (optional). Default is now |
| **limit** | `int` | No | Limit the number of results returned (optional) |
| **earliest** | `bool` | No | If True, only returns the earliest on-call for each unique combination of escalation policy, escalation level, and user. For example, if a user has multiple shifts at level 1 for a policy, only their earliest shift will be returned. This is particularly useful for determining upcoming on-call shifts or finding the next on-call for each person/level. (optional) |

#### Returns
Dict[str, Any]: A dictionary containing:
- `metadata` (Dict): Contains result count and a description of the query results.
- `oncalls` (List[Dict]): A list of parsed on-call objects.

Each on-call object contains:
- `user` (Dict): The user who is on-call, including:
    - `id` (str): User's PagerDuty ID
    - `summary` (str): User's name
    - `html_url` (str): URL to user's PagerDuty profile
- `escalation_policy` (Dict): The policy this on-call is for, including:
    - `id` (str): Policy's PagerDuty ID
    - `summary` (str): Policy name
    - `html_url` (str): URL to policy in PagerDuty
- `schedule` (Dict): The schedule that generated this on-call, including:
    - `id` (str): Schedule's PagerDuty ID
    - `summary` (str): Schedule name
    - `html_url` (str): URL to schedule in PagerDuty
- `escalation_level` (int): The escalation level for this on-call
- `start` (str): Start time of the on-call period in ISO8601 format
- `end` (str): End time of the on-call period in ISO8601 format

#### Example Response
```json
{
    "metadata": {
        "count": 13,
        "description": "Found 13 results for resource type oncalls"
    },
    "oncalls": [
        {
            "user": {
                "id": "User ID",
                "summary": "User Name",
                "html_url": "https://square.pagerduty.com/users/User ID"
            },
            "escalation_policy": {
                "id": "Escalation Policy ID",
                "summary": "Escalation Policy Name",
                "html_url": "https://square.pagerduty.com/escalation_policies/Escalation Policy ID"
            },
            "schedule": {
                "id": "Schedule ID",
                "summary": "Schedule Name",
                "html_url": "https://square.pagerduty.com/schedules/Schedule ID"
            },
            "escalation_level": 1,
            "start": "2025-03-31T18:00:00Z",
            "end": "2025-04-07T18:00:00Z"
        }
    ]
}
```

#### Example Queries
Here are common ways an LLM might want to query on-calls:

1. Find who is currently on-call for my team's escalation policies:
```python
from datetime import datetime

# Get current on-calls for the user's team's escalation policies
current_oncalls = list_oncalls()  # Uses current_user_context=True by default

# Get current time in UTC
now = datetime.utcnow()

# Filter to only show current Level 1 (primary) on-calls
primary_oncalls = [
    oncall for oncall in current_oncalls["oncalls"]
    if oncall["escalation_level"] == 1
    and datetime.fromisoformat(oncall["start"].replace("Z", "+00:00")) <= now
    and datetime.fromisoformat(oncall["end"].replace("Z", "+00:00")) > now
]

# Print current on-calls
if primary_oncalls:
    print("Current primary on-calls:")
    for oncall in primary_oncalls:
        user = oncall["user"]["summary"]
        policy = oncall["escalation_policy"]["summary"]
        schedule = oncall["schedule"]["summary"]
        print(f"- {user} is on-call for {policy} (Schedule: {schedule})")
else:
    print("No one is currently on-call")
```

2. Find who is currently on-call for a specific schedule:
```python
list_oncalls(
    current_user_context=False,  # Required when querying specific schedules
    schedule_ids=['SCHEDULE_123']  # Example PagerDuty schedule ID
)
```

3. Find who will be on-call for a schedule during a specific time range. This query may return multiple entries if the time range spans multiple on-call shifts:
```python
list_oncalls(
    current_user_context=False,  # Required when querying specific schedules
    schedule_ids=['SCHEDULE_123'],  # Example PagerDuty schedule ID
    since="2024-03-20T00:00:00Z",  # Start of time range
    until="2024-03-27T00:00:00Z"   # End of time range (1 week later)
)
```

4. Find who is currently on-call for a specific escalation policy:
```python
list_oncalls(
    current_user_context=False,  # Required when querying specific policies
    escalation_policy_ids=['ESCALATION_POLICY_123']  # Example PagerDuty escalation policy ID
)
```

5. Find who will be on-call for my team next week:
```python
from datetime import datetime, timedelta

# Get on-call shifts for next week
list_oncalls(
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=7)).isoformat()
)  # Uses current_user_context=True by default
```

6. Find who will be on-call next week for specific users:
```python
from datetime import datetime, timedelta

list_oncalls(
    current_user_context=False,  # Required when querying specific users
    user_ids=["USER_123", "USER_456"],
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=7)).isoformat()
)
```

7. Find next on-call shift for the current user:
```python
from datetime import datetime, timedelta

# Get current user's context to find their own on-call shifts
user_context = users.build_user_context()

# Query next 30 days of on-call shifts for the current user
future_shifts = list_oncalls(
    current_user_context=False,  # Required when querying specific users
    user_ids=[user_context["user_id"]],  # Current user's ID
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=30)).isoformat()
)

# Find next shift
if future_shifts["oncalls"]:
    next_shift = future_shifts["oncalls"][0]
    start_time = datetime.fromisoformat(next_shift["start"].replace("Z", "+00:00"))
    end_time = datetime.fromisoformat(next_shift["end"].replace("Z", "+00:00"))
    print(f"Next on-call shift: {start_time} to {end_time}")
else:
    print("No upcoming on-call shifts in the next 30 days")
```

8. Find all on-call shifts for a team in the next week:
```python
from datetime import datetime, timedelta

# Get current user's context
user_context = users.build_user_context()

# Query next week's on-call shifts
next_week = list_oncalls(
    escalation_policy_ids=user_context["escalation_policy_ids"],
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=7)).isoformat()
)

# Print all shifts
for shift in next_week["oncalls"]:
    user = shift["user"]["summary"]
    start = datetime.fromisoformat(shift["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(shift["end"].replace("Z", "+00:00"))
    print(f"{user} is on-call from {start} to {end}")
```

9. Find on-call shifts for a user by their name:
```python
from datetime import datetime, timedelta
from . import users

# First, find the user by name
user_query = list_users(
    current_user_context=False,  # Required when querying for arbitrary users
    query="John Smith"  # Example user name
)

# Handle potential errors
if not user_query["users"]:
    print("No users found matching the name 'John Smith'")
    exit(1)

if len(user_query["users"]) > 1:
    print("Multiple users found matching the name 'John Smith':")
    for user in user_query["users"]:
        print(f"- {user['name']} ({user['email']})")
    print("\nPlease refine your search to be more specific")
    exit(1)

# Get the user's ID from the single match
user_id = user_query["users"][0]["id"]

# Query next 30 days of on-call shifts for this user
future_shifts = list_oncalls(
    current_user_context=False,  # Required when querying specific users
    user_ids=[user_id],
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=30)).isoformat()
)

# Print all shifts
for shift in future_shifts["oncalls"]:
    start = datetime.fromisoformat(shift["start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(shift["end"].replace("Z", "+00:00"))
    print(f"On-call shift: {start} to {end}")
```

10. Find the earliest on-call shift for each user at each level in a policy:
```python
# Query next month's on-call shifts for a specific policy
next_month_shifts = list_oncalls(
    current_user_context=False,
    escalation_policy_ids=["POLICY_123"],
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=30)).isoformat(),
    earliest=True  # Get earliest shift for each user/level combination
)

# Group shifts by level to see all users at each level
shifts_by_level = {}
for shift in next_month_shifts["oncalls"]:
    level = shift["escalation_level"]
    if level not in shifts_by_level:
        shifts_by_level[level] = []
    shifts_by_level[level].append(shift)

for level, shifts in sorted(shifts_by_level.items()):
    print(f"\nLevel {level} earliest on-calls:")
    for shift in shifts:
        user = shift["user"]["summary"]
        start = datetime.fromisoformat(shift["start"].replace("Z", "+00:00"))
        print(f"- {user}'s earliest shift starts at {start}")
```

11. Find the earliest on-call shifts for each user (across all levels and policies):
```python
# Get all users in my teams
users_response = list_users()

# For each user, find their earliest shifts at each level/policy
for user in users_response["users"]:
    next_shifts = list_oncalls(
        current_user_context=False,
        user_ids=[user["id"]],
        since=datetime.utcnow().isoformat(),
        until=(datetime.utcnow() + timedelta(days=30)).isoformat(),
        earliest=True  # Get earliest shift for each level/policy combination
    )
    
    if next_shifts["oncalls"]:
        print(f"\n{user['name']}'s earliest on-call shifts:")
        for shift in next_shifts["oncalls"]:
            policy = shift["escalation_policy"]["summary"]
            level = shift["escalation_level"]
            start = datetime.fromisoformat(shift["start"].replace("Z", "+00:00"))
            print(f"- {policy} Level {level} starting at {start}")
    else:
        print(f"\n{user['name']} has no upcoming on-call shifts in the next 30 days")
```

When handling on-call queries, keep these tips in mind:

1. When answering "who is currently on-call?" questions:
   - Use current_user_context=True (default) to get the current user's team context
   - Don't specify time parameters to get current assignments
   - Check the first entry in the oncalls list for the current on-call user

2. When answering "when is my next on-call?" questions:
   - Use current_user_context=False and specify user_ids=[current_user_id]
   - Specify a future time range with since=now and until=future_date
   - Use earliest=True to get only the earliest shift for each policy/level combination
   - Remember you may get multiple shifts if the user is on different levels or policies

3. When answering "who is on-call next week?" questions:
   - Use current_user_context=True to get the team's escalation policies
   - Specify the exact time range for next week
   - Process all entries in the oncalls list as there may be multiple shifts
   - Use earliest=True if you only want the first shift for each person at each level

4. When using earliest=True:
   - You'll get one shift per unique combination of (user, policy, level)
   - If a user has multiple shifts at the same level in a policy, only their earliest shift is returned
   - A user may still appear multiple times if they're on different levels or policies
   - Results are ordered by start time within each unique combination

5. When handling escalation levels:
   - Level 1 is the primary on-call who receives initial incident notifications
   - Level 2 is the backup who gets escalated after the configured delay period
   - Level 3 serves as the final escalation path
   - When users ask about "who is on-call", they usually mean Level 1
   - When showing future rotations, consider showing all levels to give the full picture

6. When handling time ranges:
   - Always use ISO8601 format for timestamps
   - Consider timezone implications when displaying times
   - Use datetime objects for easier time manipulation and display

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

### build_user_context
Build a user context object containing the current user's permissions and access levels.

#### Parameters
None

#### Returns
Dict[str, Any]: A dictionary containing:
- `user_id` (str): The current user's PagerDuty ID
- `team_ids` (List[str]): List of team IDs the user belongs to
- `service_ids` (List[str]): List of service IDs the user has access to
- `escalation_policy_ids` (List[str]): List of escalation policy IDs the user is part of

#### Example Response
```json
{
    "user_id": "USER-1",
    "team_ids": ["TEAM-1", "TEAM-2"],
    "service_ids": ["SERVICE-1", "SERVICE-2"],
    "escalation_policy_ids": ["ESCALATION-POLICY-1"]
}
```

#### Example Usage
```python
from pagerduty_mcp_server import users

# Get the current user's context
user_context = users.build_user_context()

# Use the context to filter queries
incidents = list_incidents(current_user_context=False, team_ids=user_context["team_ids"])
```

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
