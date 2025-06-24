# PagerDuty MCP Tools
The MCP server tools below expose PagerDuty API functionality to LLMs. These tools are designed to be used programmatically, with structured inputs and outputs.

## General Information
The following general information in this sectionapplies to all tools.

### Timestamp Format
- All timestamps MUST be in ISO8601 format (YYYY-MM-DDTHH:MM:SSZ), for example `2025-02-26T00:00:00Z`
- The `since` and `until` parameters MUST be in ISO8601 format for all tools
- Relative time references like "now" MUST NOT be used for any parameters

### Best Practices
- Prefer using default parameters when they align with the user's intent
- When retrieving user-specific data, prefer querying with the default `current_user_context=True` rather than explicitly querying by user ID
- Minimize the number of API calls by using the most efficient query parameters
- If a tool call returns an error, check the documentation for examples and supported parameters and consider if removing parameters might resolve the error before adding more parameters

## Escalation Policy Tools
Tools for interacting with PagerDuty Escalation Policies. An Escalation Policy determines what User or Schedule will be Notified and in what order when an Incident is triggered.

### get_escalation_policies
Get PagerDuty escalation policies by filters or get details for a specific policy ID.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| policy_id | `str` | No | The escalation policy ID to retrieve. Cannot be used with any other parameters. |
| current_user_context | `bool` | No | If `True`, filters escalation policies to those associated with the current user (via `user_id` and `team_ids`). Cannot be used with `user_ids` or `team_ids`. |
| query | `str` | No | Filter escalation policies by name (case-insensitive substring match). |
| user_ids | `List[str]` | No | Filter results to escalation policies that include any of the given user IDs. Cannot be used with `current_user_context`. |
| team_ids | `List[str]` | No | Filter results to escalation policies that belong to any of the given teams. Cannot be used with `current_user_context`. |
| limit | `int` | No | Limit the number of results returned. |

#### Returns
Each escalation policy object contains:
- `id` (str): The unique identifier for the escalation policy.
- `name` (str): The name of the escalation policy.
- `summary` (str): The summary of the escalation policy.
- `escalation_rules` (List[Dict]): A list of escalation rules, each containing:
  - `id` (str): The unique identifier for the escalation rule.
  - `escalation_delay_in_minutes` (int): Delay before running escalation rule
  - `targets` (List[Dict]): A list of escalation targets, each containing:
    - `id` (str): Target ID
    - `type` (str): Target type (e.g., "user_reference", "schedule_reference")
    - `summary` (str): Target name or description
- `services` (List[Dict]): A list of services using the escalation policy, each containing only:
  - `id` (str): Service ID
- `teams` (List[Dict]): A list of teams using the escalation policy, each containing:
  - `id` (str): Team ID
  - `summary` (str): Team name
- `description` (str): Description of the escalation policy.

#### Example Response
When listing escalation policies:
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type escalation_policies"
    },
    "escalation_policies": [
        {
          "id": "POLICY-1",
          "name": "Test Escalation Policy 1",
          "escalation_rules": [...],
          "services": [...],
          "teams": [...],
          "description": "policy description"
        },
    ]
}
```

When getting a specific escalation policy:
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type escalation_policy"
    },
    "escalation_policies": [
        {
          "id": "POLICY-1",
          "name": "Test Escalation Policy 1",
          "escalation_rules": [...],
          "services": [...],
          "teams": [...]
        }
    ]
}
```

#### Example Queries
```python
# Get escalation policies for the current user's teams
get_escalation_policies()

# Get escalation policies for a specific team
get_escalation_policies(current_user_context=False, team_ids=["TEAM_123"])

# Get escalation policies for a specific user
get_escalation_policies(current_user_context=False, user_ids=["USER_123"])

# Search for escalation policies by name
get_escalation_policies(query="SEARCH_STRING")

# Get details for a specific escalation policy
get_escalation_policies(policy_id="POLICY_123")
```

## Incidents Tools
Tools for interacting with PagerDuty incidents. An Incident represents a problem or an issue that needs to be addressed and resolved. Incidents can be triggered, acknowledged, or resolved, and are assigned to a User based on the Service's Escalation Policy.

### get_incidents
Get PagerDuty incidents by filters or get details for a specific incident ID or number.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| incident_id | `str` | No | Incident ID or number to show details for. Cannot be used with other parameters except include_* flags. |
| current_user_context | `bool` | No | If `True`, filters incidents to those associated with the current user's teams and services. Cannot be used with `team_ids` or `service_ids`. |
| service_ids | `List[str]` | No | Filter incidents by specific service IDs. Cannot be used with `current_user_context`. |
| team_ids | `List[str]` | No | Filter incidents by specific team IDs. Cannot be used with `current_user_context`. |
| statuses | `List[str]` | No | Filter incidents by status. Must be input as a list of strings, valid values are `["triggered", "acknowledged", "resolved"]`. Defaults to all three. |
| since | `str` | No | Start of date range in ISO8601 format. Default range: 1 month, max range: 6 months. |
| until | `str` | No | End of date range in ISO8601 format. Default range: 1 month, max range: 6 months. |
| limit | `int` | No | Limit the number of results returned. |
| include_past_incidents | `bool` | No | If `True` and `incident_id` is provided, includes similar past incidents. Defaults to `False`. |
| include_related_incidents | `bool` | No | If `True` and `incident_id` is provided, includes related incidents. Defaults to `False`. |
| include_notes | `bool` | No | If `True` and `incident_id` is provided, includes notes for the incident. Defaults to `False`. |

#### Returns
Each incident object contains:
- `id` (str): The unique identifier for the incident.
- `incident_number` (int): The incident number.
- `title` (str): The title of the incident.
- `status` (str): Current status of the incident.
- `urgency` (str): Current urgency level of the incident.
- `priority` (Dict): Priority information.
- `created_at` (str): Timestamp of incident creation.
- `updated_at` (str): Timestamp of last update.
- `resolved_at` (str): Timestamp of resolution (if resolved).
- `resolve_reason` (str): Reason for resolution (if resolved).
- `assignments` (List[Dict]): List of assignments, each containing:
  - `assignee` (Dict): Information about the assignee, containing:
    - `id` (str): Assignee's PagerDuty ID
    - `summary` (str): Assignee's name
  - `at` (str): Timestamp of assignment
- `acknowledgements` (List[Dict]): List of acknowledgments, each containing:
  - `acknowledger` (Dict): Information about the acknowledger, containing:
    - `id` (str): Acknowledger's PagerDuty ID
    - `summary` (str): Acknowledger's name
  - `at` (str): Timestamp of acknowledgment
- `service` (Dict): The service this incident belongs to, containing only:
  - `id` (str): Service's PagerDuty ID
- `teams` (List[Dict]): List of teams associated with this incident, each containing:
  - `id` (str): Team's PagerDuty ID
  - `summary` (str): Team's name
- `alert_counts` (Dict): Counts of alerts for this incident.
- `summary` (str): Summary of the incident.
- `description` (str): Description of the incident.
- `escalation_policy` (Dict): The escalation policy for this incident, containing:
  - `id` (str): Escalation policy's PagerDuty ID
  - `summary` (str): Escalation policy's name
- `incident_key` (str): Unique incident key.
- `last_status_change_at` (str): Timestamp of last status change.
- `last_status_change_by` (Dict): User who last changed status, containing:
  - `id` (str): User's PagerDuty ID
  - `summary` (str): User's name
- `body_details` (Dict): Incident body details containing monitor information, query, and tags.

Additional fields present when optional parameters are used:
- `past_incidents` (List[Dict], optional): Only present if `include_past_incidents=True`. List of similar past incidents, each containing:
  - Same fields as the standard incident object
  - `similarity_score` (float): Score indicating how similar this incident is to the current one
- `related_incidents` (List[Dict], optional): Only present if `include_related_incidents=True`. List of related incidents, each containing:
  - Same fields as the standard incident object
  - `relationship_type` (str): Type of relationship (e.g., "machine_learning_inferred")
  - `relationship_metadata` (Dict): Additional metadata about the relationship
- `notes` (List[Dict], optional): Only present if `include_notes=True`. List of notes for the incident, each containing:
  - `id` (str): The unique identifier for the note
  - `content` (str): The content/text of the note
  - `created_at` (str): Timestamp when the note was created
  - `user` (Dict): Information about the user who created the note:
    - `id` (str): The user's PagerDuty ID
    - `name` (str): The user's name
    - `type` (str): The type of user (user_reference/bot_user_reference)
  - `channel` (Dict): Information about how the note was created:
    - `summary` (str): Description of the channel (e.g., "The PagerDuty website or APIs")
    - `type` (str): The type of channel

#### Raises
- `ValueError`: If:
  - `incident_id` is used along with any other query parameters (Note: `include_past_incidents` and `include_related_incidents` are allowed with `incident_id`).
  - `current_user_context` is True and `service_ids` or `team_ids` are provided (and `incident_id` is not provided).
  - `current_user_context` is False and neither `service_ids` nor `team_ids` are provided (and `incident_id` is not provided).
  - `statuses` contains invalid values (must be one of: `triggered`, `acknowledged`, `resolved`) or is not a list of strings (and `incident_id` is not provided).
  - `since` or `until` are not valid ISO8601 timestamps (and `incident_id` is not provided).
  - `incident_id` is not provided, but `include_past_incidents`, `include_related_incidents`, or `include_notes` is set to `True`.
- `RuntimeError`: If the API request fails or response processing fails

#### Example Response
When listing incidents:
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
            "incident_number": 1,
            "title": "Test Incident 1",
            "status": "triggered",
            "urgency": "high",
            "priority": {...},
            "created_at": "2024-03-14T12:00:00Z",
            "updated_at": "2024-03-14T12:00:00Z",
            "resolved_at": null,
            "resolve_reason": null,
            "assignments": [...],
            "acknowledgements": [...],
            "service": {"id": "SERVICE-1"},
            "teams": [...],
            "alert_counts": {...},
            "summary": "Test Incident 1",
            "description": "Test incident description",
            "escalation_policy": {"id": "POLICY-1"},
            "incident_key": "INCIDENT-1",
            "last_status_change_at": "2024-03-14T12:00:00Z",
            "last_status_change_by": null
        }
    ]
}
```

When requesting a specific incident with optional includes:
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type incident",
        "past_incidents_count": 1,
        "related_incidents_count": 1,
        "notes_count": 1
    },
    "incidents": [
        {
            "id": "INCIDENT-XYZ",
            "incident_number": 2,
            "title": "Specific Incident",
            "status": "acknowledged",
            "urgency": "high",
            "priority": {...},
            "created_at": "2024-03-14T12:00:00Z",
            "updated_at": "2024-03-14T12:00:00Z",
            "resolved_at": null,
            "resolve_reason": null,
            "assignments": [...],
            "acknowledgements": [...],
            "service": {...},
            "teams": [...],
            "alert_counts": {...},
            "summary": "Specific Incident Details",
            "description": "Specific incident description",
            "escalation_policy": {...},
            "incident_key": "INCIDENT-XYZ",
            "last_status_change_at": "2024-03-14T12:00:00Z",
            "last_status_change_by": null,
            "body_details": {...},
            "past_incidents": [
                {
                    "id": "PAST_INCIDENT_A",
                    "summary": "Similar Past Incident A",
                    "similarity_score": 150.75
                }
            ],
            "related_incidents": [
                {
                    "id": "RELATED_INCIDENT_B",
                    "summary": "Related Incident B",
                    "relationship_type": "machine_learning_inferred",
                    "relationship_metadata": {
                        "grouping_classification": "similar_contents",
                        "user_feedback": {"positive_feedback_count": 5, "negative_feedback_count": 0}
                    }
                }
            ],
            "notes": [
                {
                    "id": "NOTE_1",
                    "content": "This is a note on the incident",
                    "created_at": "2024-03-14T14:00:00Z",
                    "user": {
                        "id": "USER_A",
                        "name": "User A",
                        "type": "user_reference"
                    },
                    "channel": {
                        "summary": "The PagerDuty website or APIs",
                        "type": "web"
                    }
                }
            ]
        }
    ]
}
```

#### Example Queries
```python
# Get all incidents for current user's teams (including resolved)
# Use this query to answer questions like "What incidents have I been assigned this week?" or "How many incidents have I been alerted on?"
get_incidents()  # Uses defaults: current_user_context=True, all statuses

# Get incidents from a specific time range
get_incidents(since="2025-02-26T00:00:00Z", until="2025-03-26T00:00:00Z")

# Get incidents for specific services
# Use this query to answer questions like "What incidents have been resolved this week for Service 123?"
get_incidents(
    current_user_context=False,
    service_ids=["SERVICE_123"],
    statuses=["resolved"]
)

# Get details for a specific incident with additional context
get_incidents(
    incident_id="INCIDENT_ABC",
    include_past_incidents=True,
    include_related_incidents=True,
    include_notes=True
)
```

## On-Call Tools
Tools for interacting with PagerDuty On-Calls. An On-Call represents a contiguous unit of time for which a User will be On-Call for a given Escalation Policy and Escalation Rule.

### Escalation Levels Explained
- Level 1: Primary on-call. Receives initial incident notifications.
- Level 2: Backup on-call. Receives escalated incidents if Level 1 doesn't respond.
- Level 3: Final escalation path. Typically the last resort if lower levels don't respond.

### get_oncalls
List the on-call entries during a given time range.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| current_user_context | `bool` | No | If `True`, shows on-calls for all escalation policies associated with the current user's teams. Cannot be used with `user_ids`. (default: True) |
| schedule_ids | `List[str]` | No | Return only on-calls for the specified schedule IDs |
| user_ids | `List[str]` | No | Return only on-calls for the specified user IDs. Cannot be used with current_user_context |
| escalation_policy_ids | `List[str]` | No | Return only on-calls for the specified escalation policy IDs |
| since | `str` | No | Start of date range in ISO8601 format. Default is current datetime. |
| until | `str` | No | End of date range in ISO8601 format. Default is current datetime, max range: 90 days in the future. Cannot be before `since`. |
| limit | `int` | No | Limit the number of results returned |
| earliest | `bool` | No | If True, only returns the earliest on-call for each unique combination of escalation policy, escalation level, and user |

#### Returns
Each on-call object contains:
- `user` (Dict): The user who is on-call, containing:
    - `id` (str): User's PagerDuty ID
    - `summary` (str): User's name
- `escalation_policy` (Dict): The policy this on-call is for, containing:
    - `id` (str): Policy's PagerDuty ID
    - `summary` (str): Policy's name
- `schedule` (Dict): The schedule that generated this on-call, containing:
    - `id` (str): Schedule's PagerDuty ID
    - `summary` (str): Schedule's name
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
                "id": "USER-1"
            },
            "escalation_policy": {
                "id": "POLICY-1"
            },
            "schedule": {
                "id": "SCHEDULE-1"
            },
            "escalation_level": 1,
            "start": "2025-03-31T18:00:00Z",
            "end": "2025-04-07T18:00:00Z"
        }
    ]
}
```

#### Example Queries
```python
# Find who is currently on-call for my team's escalation policies
get_oncalls()

# Find who is currently on-call for a specific schedule
get_oncalls(current_user_context=False, schedule_ids=['SCHEDULE_123'])

# Find the next on-call shift for the current user
from datetime import datetime, timedelta
user_context = build_user_context()
get_oncalls(
    current_user_context=False,
    user_ids=[user_context["user_id"]],
    since=datetime.utcnow().isoformat(),
    until=(datetime.utcnow() + timedelta(days=30)).isoformat(),
    earliest=True
)
```

## Schedule Tools
Tools for interacting with PagerDuty schedules. A Schedule determines the time periods that Users are On-Call.

### get_schedules
Get PagerDuty schedules by filters or get details for a specific schedule ID.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| schedule_id | `str` | No | The schedule ID to retrieve details for. Cannot be used with `query` or `limit`. |
| query | `str` | No | Filter schedules whose names contain the search query (case-insensitive substring match). |
| limit | `int` | No | Limit the number of results returned. |
| since | `str` | No | Start time for overrides/final schedule details (ISO8601). Only used if `schedule_id` is provided. Default range: 2 weeks before `until` if `until` is provided. |
| until | `str` | No | End time for overrides/final schedule details (ISO8601). Only used if `schedule_id` is provided. Default range: 2 weeks after `since` if `since` is provided. |

#### Returns
Each schedule object contains:
- `id` (str): The unique identifier for the schedule.
- `name` (str): The name of the schedule.
- `summary` (str): Summary of the schedule.
- `description` (str): Description of the schedule.
- `time_zone` (str): The time zone for the schedule.
- `escalation_policies` (List[Dict]): List of escalation policies, each containing:
  - `id` (str): Policy's PagerDuty ID
  - `summary` (str): Policy's name
- `teams` (List[Dict]): List of teams this schedule is assigned to, each containing:
  - `id` (str): Team's PagerDuty ID
  - `summary` (str): Team's name
- `schedule_layers` (List[Dict]): List of schedule layers, each containing:
  - `id` (str): Layer ID
  - `name` (str): Layer name
  - `start` (str): Start time
  - `end` (str): End time
  - `users` (List[Dict]): List of users in this layer, each containing:
    - `id` (str): User's PagerDuty ID
    - `summary` (str): User's name
- `final_schedule` (Dict, optional): If `schedule_id` and `since`/`until` are provided, contains the computed schedule entries for the specified time range.
  - `rendered_schedule_entries` (List[Dict]): List of computed entries, each containing:
    - `start` (str): Start time of the entry (ISO8601).
    - `end` (str): End time of the entry (ISO8601).
    - `user` (Dict): Information about the user on call:
      - `id` (str): User ID.
      - `summary` (str): User name.
- `overrides` (List[Dict], optional): If `schedule_id` and `since`/`until` are provided, contains any overrides within the specified time range. Each override includes:
  - `start` (str): Start time of the override (ISO8601).
  - `end` (str): End time of the override (ISO8601).
  - `user` (Dict): Information about the user taking the override.

#### Example Response
When listing schedules:
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type schedules"
    },
    "schedules": [
        {
            "id": "SCHEDULE-1",
            "name": "Test Schedule 1",
            "summary": "Test Schedule 1",
            "description": "Test schedule description",
            "time_zone": "UTC",
            "escalation_policies": [...],
            "teams": [...]
        },
        {
            "id": "SCHEDULE-2",
            "name": "Test Schedule 2",
            // ... other fields ...
        }
    ]
}
```

When getting a specific schedule:
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type schedule"
    },
    "schedules": [
        {
            "id": "SCHEDULE-1",
            "name": "Test Schedule 1",
            "summary": "Test Schedule 1",
            "description": "Test schedule description",
            "time_zone": "UTC",
            "escalation_policies": [...],
            "teams": [...]
            // Optional fields 'final_schedule' and 'overrides' may appear here if 'since'/'until' were provided
        }
    ]
}
```

When getting a specific schedule with `since`/`until`:
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type schedule"
    },
    "schedules": [
        {
            "id": "SCHEDULE-1",
            // ... other schedule fields ...
            "final_schedule": {
                "rendered_schedule_entries": [
                    {
                        "start": "2024-03-25T18:00:00Z",
                        "end": "2024-04-01T18:00:00Z",
                        "user": { "id": "USER_A", "summary": "User A" }
                    },
                    {
                        "start": "2024-04-01T18:00:00Z",
                        "end": "2024-04-08T18:00:00Z",
                        "user": { "id": "USER_B", "summary": "User B" }
                    }
                ]
            },
            "overrides": [
                {
                    "start": "2024-03-27T10:00:00Z",
                    "end": "2024-03-28T10:00:00Z",
                    "user": { "id": "USER_C", "summary": "User C" }
                }
            ]
        }
    ]
}
```

#### Example Queries
```python
# List all schedules
get_schedules()

# Search for schedules by name
get_schedules(query="Schedule Name")

# Get schedule details with on-call information for a date range
get_schedules(
    schedule_id="SCHEDULE_123",
    since="2025-02-27T00:00:00Z",
    until="2025-03-13T00:00:00Z"
)
```

### list_users_oncall
List the users on call for a schedule during the specified time range.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| schedule_id | `str` | Yes | The ID of the schedule to query |
| since | `str` | No | Start of date range in ISO8601 format (optional) |
| until | `str` | No | End of date range in ISO8601 format (optional) |

#### Returns
A list of user on-call entries, each containing:
- `user` (Dict): Information about the user on call:
  - `id` (str): User's PagerDuty ID
  - `summary` (str): User's name
  - `email` (str): User's email address
- `start` (str): Start time of the on-call shift in ISO8601 format
- `end` (str): End time of the on-call shift in ISO8601 format

#### Example Response
```json
{
    "metadata": {
        "count": 3,
        "description": "Found 3 users on call for schedule SCHEDULE-123"
    },
    "users_oncall": [
        {
            "user": {
                "id": "USER-1",
                "summary": "John Doe",
                "email": "john.doe@example.com"
            },
            "start": "2025-03-25T18:00:00Z",
            "end": "2025-04-01T18:00:00Z"
        },
        {
            "user": {
                "id": "USER-2",
                "summary": "Jane Smith",
                "email": "jane.smith@example.com"
            },
            "start": "2025-04-01T18:00:00Z",
            "end": "2025-04-08T18:00:00Z"
        }
    ]
}
```

#### Example Queries
```python
# Get users on call for a schedule for the default time range
list_users_oncall(schedule_id="SCHEDULE_123")

# Get users on call for a schedule for a specific time range
list_users_oncall(
    schedule_id="SCHEDULE_123",
    since="2025-03-01T00:00:00Z",
    until="2025-04-01T00:00:00Z"
)
```

## Service Tools
Tools for interacting with PagerDuty Services. A Service represents an entity you monitor (such as a web Service, email Service, or database Service.) It is a container for related Incidents that associates them with Escalation Policies.

### get_services
Get PagerDuty services by filters or get details for a specific service ID.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | `str` | No | The service ID to retrieve. Cannot be used with any other parameters. |
| current_user_context | `bool` | No | If `True`, filters services to those associated with the current user's teams. Cannot be used with `team_ids`. |
| team_ids | `List[str]` | No | Filter services by specific team IDs. Cannot be used with `current_user_context`. |
| query | `str` | No | Filter services whose names contain the search query. |
| limit | `int` | No | Limit the number of results returned. |

#### Returns
Each service object contains:
- `id` (str): The unique identifier for the service.
- `name` (str): The name of the service.
- `description` (str): Description of the service.
- `status` (str): Current status of the service.
- `created_at` (str): Timestamp of service creation.
- `updated_at` (str): Timestamp of last update.
- `teams` (List[Dict]): List of teams this service belongs to, each containing:
  - `id` (str): Team's PagerDuty ID
  - `summary` (str): Team's name
- `integrations` (List[Dict]): List of integrations for this service, each containing:
  - `id` (str): Integration's PagerDuty ID
  - `summary` (str): Integration's name

#### Example Response
When listing services:
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type services"
    },
    "services": [
        {
            "id": "SERVICE-1",
            "name": "Test Service 1",
            "description": "Test service description",
            "status": "active",
            "created_at": "2024-03-14T12:00:00Z",
            "updated_at": "2024-03-14T12:00:00Z",
            "teams": [...],
            "integrations": [...]
        },
        {
            "id": "SERVICE-2",
            "name": "Test Service 2",
            // ... other fields ...
        }
    ]
}
```

When getting a specific service (with `service_id`):
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type service" 
    },
    "services": [
        {
            "id": "SERVICE-1",
            "name": "Test Service 1",
            "description": "Test service description",
            "status": "active",
            "created_at": "2024-03-14T12:00:00Z",
            "updated_at": "2024-03-14T12:00:00Z",
            "teams": [...],
            "integrations": [...]
        }
    ]
}
```

#### Example Queries
```python
# List services for the current user's teams
get_services()

# List services for a specific team
get_services(current_user_context=False, team_ids=['TEAM_123'])

# Get details for a specific service
get_services(service_id="SERVICE_123")

# Search for services by name
get_services(query="Payment Processing")
```

## Team Tools
Tools for interacting with PagerDuty teams. A Team is a collection of Users and Escalation Policies.

### get_teams
Get PagerDuty teams by filters or get details for a specific team ID.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| team_id | `str` | No | The team ID to retrieve. Cannot be used with any other parameters. |
| query | `str` | No | Filter teams whose names contain the search query. |
| limit | `int` | No | Limit the number of results returned. |

#### Returns
Each team object contains:
- `id` (str): The unique identifier for the team.
- `name` (str): The name of the team.
- `description` (str): Description of the team.
- `type` (str): The team type.
- `summary` (str): The team summary.
- `default_role` (str): Default role for team members.
- `parent` (Dict, optional): If this is a sub-team, contains information about the parent team:
  - `id` (str): Parent team's PagerDuty ID
  - `type` (str): Parent team's type

#### Example Response
When listing teams:
```json
{
    "metadata": {
        "count": 2,
        "description": "Found 2 results for resource type teams"
    },
    "teams": [
        {
            "id": "TEAM-1",
            "name": "Test Team 1",
            "description": "Test team description",
            "type": "team",
            "summary": "Test Team 1"
        },
        {
            "id": "TEAM-2",
            "name": "Test Team 2",
            "description": "Another team description",
            "type": "team",
            "summary": "Test Team 2"
        }
    ]
}
```

When getting a specific team:
```json
{
    "metadata": {
        "count": 1,
        "description": "Found 1 result for resource type team"
    },
    "teams": [
        {
            "id": "TEAM-1",
            "name": "Test Team 1",
            "description": "Test team description",
            "type": "team",
            "summary": "Test Team 1",
            "default_role": "user",
            "parent": null
        }
    ]
}
```

#### Example Queries
```python
# List all teams
get_teams()

# Search for teams by name
get_teams(query="Team Name")

# Get details for a specific team
get_teams(team_id="TEAM_123")
```

## User Tools
Tools for interacting with PagerDuty users.

### build_user_context
Build a user context object containing the current user's permissions and access levels.

#### Returns
Dict[str, Any]: A dictionary containing:
- `user_id` (str): The current user's PagerDuty ID
- `name` (str): The current user's full name
- `email` (str): The current user's email address
- `team_ids` (List[str]): List of team IDs the user belongs to
- `service_ids` (List[str]): List of service IDs the user has access to
- `escalation_policy_ids` (List[str]): List of escalation policy IDs the user is part of

#### Example Response
```json
{
    "user_id": "USER-1",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "team_ids": ["TEAM-1", "TEAM-2"],
    "service_ids": ["SERVICE-1", "SERVICE-2"],
    "escalation_policy_ids": ["ESCALATION-POLICY-1"]
}
```

### get_users
Get PagerDuty users by filters or get details for a specific user ID.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | `str` | No | The user ID to retrieve. Cannot be used with other parameters. |
| current_user_context | `bool` | No | If `True`, filters users to those associated with the current user's teams. Cannot be used with `team_ids`. |
| team_ids | `List[str]` | No | Filter users by specific team IDs. Cannot be used with `current_user_context`. |
| query | `str` | No | Filter users whose names contain the search query. |
| limit | `int` | No | Limit the number of results returned. |

#### Returns
Each user object contains:
- `id` (str): The unique identifier for the user.
- `name` (str): The user's full name.
- `email` (str): The user's email address.
- `description` (str): Description of the user.
- `type` (str): The type of user.
- `teams` (List[Dict]): List of teams the user belongs to, each containing:
  - `id` (str): Team's PagerDuty ID
  - `type` (str): Team type
  - `summary` (str): Team's name
- `contact_methods` (List[Dict]): List of contact methods for notifications, each containing:
  - `id` (str): Contact method ID
  - `type` (str): Contact method type
  - `summary` (str): Contact method description (e.g., "Default", "Mobile", "iPhone")
- `notification_rules` (List[Dict]): List of notification rules, each containing:
  - `id` (str): Rule ID
  - `type` (str): Rule type

#### Example Queries
```python
# List users for current user's teams
get_users()

# List users for a specific team
get_users(current_user_context=False, team_ids=["TEAM_123"])

# Search for users by name
get_users(query="John")

# Get details for a specific user
get_users(user_id="USER_123")
```