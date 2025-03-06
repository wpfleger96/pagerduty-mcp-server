# PagerDuty MCP Tools

## Escalation Policy Tools
Tools for interacting with PagerDuty Escalation Policies. An Escalation Policy determines what User or Schedule will be Notified and in what order. This will happen when an Incident is triggered. Escalation Policies can be used by one or more Services.

### list_escalation_policies
List existing escalation policies with optional filtering parameters.

When answering questions like "show me current escalation policies" where the prompt does not specify any team_ids or user_ids, you should assume to filter incidents based on the current user's ids and team_ids.

#### Parameters
- `query` (optional): Filter escalation policies whose names contain the search query
- `user_ids` (optional): Filter results to only escalation policies that include the given user IDs
- `team_ids` (optional): Filter results to only escalation policies assigned to teams with the given IDs
- `include` (optional): Array of additional details to include. Options: teams,services,num_loops,current_state
- `sort_by` (optional): Sort result by the given field. Options: name,description
- `use_my_teams` (optional): Boolean, when true uses the current user's team context
  - Default: `true`
  - When true, `team_ids` must not be provided
  - When false, `team_ids` must be provided

#### Returns
List[Dict[str, Any]]: List of escalation policy objects matching the specified criteria

#### Example Queries
Here are common ways an LLM might want to query escalation policies:
```python
TODO
```

### get_escalation_policy
Get detailed information about a specific escalation policy.

#### Parameters
- `policy_id`: The ID of the escalation policy to get
- `include` (optional): Array of additional details to include. Options: teams,services,num_loops,current_state

#### Returns
Dict[str, Any]: Escalation policy object with detailed information

## Incidents Tools
Tools for interacting with PagerDuty incidents. An Incident represents a problem or an issue that needs to be addressed and resolved.
Incidents can be thought of as a problem or an issue within your Service that needs to be addressed and resolved, they are normalized and de-duplicated.
Incidents can be triggered, acknowledged, or resolved, and are assigned to a User based on the Service's Escalation Policy.
A triggered Incident prompts a Notification to be sent to the current On-Call User(s) as defined in the Escalation Poicy used by the Service.
Incidents are triggered through the Events API or are created by Integrations.

Note that the default API behavior is to exclude incidents with status "resolved" so when answering questions like "How many incidents were generated this week?", your API query should include "resolved" incidents. When answering questions like "How many incidents were generated this week?" where the prompt does not specify any team_ids or service_ids, you should assume to filter incidents based on the current user's teams and services.

### list_incidents
List PagerDuty incidents with optional filtering parameters.

#### Parameters
- `service_ids` (optional): List of PagerDuty service IDs to filter by
- `team_ids` (optional): List of PagerDuty team IDs to filter by
- `statuses` (optional): List of incident statuses to include. Valid values:
  - `triggered` - Active and unacknowledged incidents
  - `acknowledged` - Active but acknowledged incidents
  - `resolved` - Resolved incidents
  - Default: `["triggered", "acknowledged"]`
- `use_my_teams` (optional): Boolean, when true uses the current user's team context
  - Default: `true`
  - When true, `service_ids` and `team_ids` must not be provided
  - When false, either `service_ids` or `team_ids` must be provided
- `date_range` (optional): Special value that affects date filtering
  - When set to `"all"`, ignores `since` and `until` parameters
- `since` (optional): ISO8601 timestamp for start of date range
  - Example: `"2025-03-01T00:00:00Z"`
  - Default: 1 month ago (provided by PagerDuty API)
- `until` (optional): ISO8601 timestamp for end of date range
  - Example: `"2025-03-05T00:00:00Z"`
  - Default: current time (provided by PagerDuty API)

#### Returns
List[Dict[str, Any]]: List of incident objects matching the specified criteria

#### Example Queries
Here are common ways an LLM might want to query incidents:

1. Get all active incidents for the current user's teams:
```python
list_incidents()  # Uses defaults: use_my_teams=True, statuses=["triggered", "acknowledged"]
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
    use_my_teams=False,
    service_ids=["P8PP81X"],
    statuses=["triggered", "acknowledged"]
)
```

4. Get all incidents regardless of date:
```python
list_incidents(
    date_range="all",
    statuses=["triggered", "acknowledged", "resolved"]
)
```

### get_incident
Get detailed information about the given incident.

#### Parameters
- `id`: the ID of the incident to get

#### Returns
Dict[str, Any]: Incident object with detailed information

## On-Call Tools
Tools for interacting with PagerDuty On-Calls. An On-Call represents a contiguous unit of time for which a User will be On-Call for a given Escalation Policy and Escalation Rule.
This may be the result of that User always being On-Call for the Escalation Rule, or a block of time during which the computed result of a Schedule on that Escalation Rule puts the User On-Call.
During an On-Call, the User is expected to bear responsibility for responding to any Notifications they receives and working to resolve the associated Incident(s).
On-Calls cannot be created directly through the API; they are the computed result of how Escalation Policies and Schedules are configured. The API provides read-only access to the On-Calls generated by PagerDuty.

When answering questions like "Who is the current oncall?" where the prompt does not specify any schedule_ids, user_ids, or escalation_policy_ids, you should assume to filter On-Calls based on the current user's schedules and escalation policies.

### list_oncall
List the on-call entries during a given time range.

#### Parameters
- `schedule_ids` (optional): Return only on-calls for the specified schedule IDs
- `user_ids` (optional): Return only on-calls for the specified user IDs
- `escalation_policy_ids` (optional): Return only on-calls for the specified escalation policy IDs
- `since` (optional): The start of the time range over which you want to search
- `until` (optional): The end of the time range over which you want to search
- `include` (optional): Array of additional details to include. Options: users,schedules,escalation_policies

#### Returns
List[Dict[str, Any]]: List of on-call entries matching the specified criteria

## Schedule Tools
Tools for interacting with PagerDuty schedules. A Schedule determines the time periods that Users are On-Call.
Only On-Call Users are eligible to receive Notifications from Incidents.
The details of the On-Call Schedule specify which single User is On-Call for that Schedule at any given point in time.
An On-Call Schedule consists of one or more Schedule Layers that rotate a group of Users through the same shift at a set interval.
Schedules are used by Escalation Policies as an escalation target for a given Escalation Rule.

### list_schedules
List the on-call schedules with optional filtering parameters.

#### Parameters
- `query` (optional): Filter schedules whose names contain the search query
- `include` (optional): Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers

#### Returns
List[Dict[str, Any]]: List of schedule objects

### get_schedule
Get detailed information about a given schedule.

#### Parameters
- `schedule_id`: The ID of the schedule to get
- `since` (optional): The start of the time range over which you want to search
- `until` (optional): The end of the time range over which you want to search
- `include` (optional): Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers

#### Returns
Dict[str, Any]: Schedule object with detailed information

## Service Tools
Tools for interacting with PagerDuty Services. A Service represents an entity you monitor (such as a web Service, email Service, or database Service.)
It is a container for related Incidents that associates them with Escalation Policies.
A Service is the focal point for Incident management; Services specify the configuration for the behavior of Incidents triggered on them.

### list_services
List existing PagerDuty services with optional filtering parameters.

#### Parameters
- `team_ids` (optional): Filter results to only services assigned to teams with the given IDs
- `include` (optional): Array of additional details to include. Options: escalation_policy,teams
- `query` (optional): Filter services whose names contain the search query

#### Returns
List[Dict[str, Any]]: List of service objects matching the specified criteria

### get_service
Get detailed information about a given service.

#### Parameters
- `service_id`: The ID of the service to get
- `include` (optional): Array of additional details to include. Options: escalation_policy,teams

#### Returns
Dict[str, Any]: Service object with detailed information

## Team Tools

### list_teams
List teams in your PagerDuty account.

#### Parameters
- `query` (optional): Filter teams whose names contain the search query
- `include` (optional): Array of additional details to include. Options: members,notification_rules

#### Returns
List[Dict[str, Any]]: List of team objects matching the specified criteria

### get_team
Get detailed information about a given team.

#### Parameters
- `team_id`: The ID of the team to get
- `include` (optional): Array of additional details to include. Options: members,notification_rules

#### Returns
Dict[str, Any]: Team object with detailed information

## User Tools

### show_current_user
Get the current user's PagerDuty profile.

#### Parameters
None

#### Returns
Dict[str, Any]: The user object containing profile information

### get_user_context
Fetches the user's team memberships and then queries for all services associated with those teams.

#### Parameters
None

#### Returns
tuple[List[str], List[str]]: A tuple of (team_ids, service_ids)

# Natural Language Examples
The tools are designed to handle natural language queries like:

- "Show me all active incidents"
- "List incidents from my teams"
- "Show me resolved incidents from the last week"
- "Get all incidents from service P8PP81X"
- "Show me all incidents regardless of date"
- "Who is on-call right now?"
- "Show me the on-call schedule for next week"
- "List all services in my team"
- "Get details about the service named 'Production API'"
- "Show me all escalation policies"
- "List members of the Infrastructure team"

LLMs should translate these requests into appropriate parameter combinations using the examples above as a guide.