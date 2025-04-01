"""PagerDuty MCP Server main module."""

import logging
from typing import List, Dict, Any, Optional, Union

from mcp.server.fastmcp import FastMCP

from . import escalation_policies
from . import incidents
from . import oncalls
from . import schedules
from . import services
from . import teams
from . import users

logger = logging.getLogger(__name__)
server = FastMCP(
    name="pagerduty_mcp_server",
    log_level="INFO"
)

"""
Escalation Policies Tools
"""
@server.tool()
def list_escalation_policies(*,
                            current_user_context: bool = True,
                            query: Optional[str] = None,
                            user_ids: Optional[List[str]] = None,
                            team_ids: Optional[List[str]] = None,
                            limit: Optional[int] = None) -> Dict[str, Any]:
    """List existing escalation policies based on the given criteria.

    Args:
        current_user_context (bool): Whether to use the current user's ID/team IDs context (default: True, cannot be used with user_ids or team_ids)
        query (str): Filter escalation policies whose names contain the search query (optional)
        user_ids (List[str]): Filter results to only escalation policies that include the given user IDs (optional, cannot be used with current_user_context)
        team_ids (List[str]): Filter results to only escalation policies assigned to teams with the given IDs (optional, cannot be used with current_user_context)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of escalation policies matching the specified criteria
    """
    if current_user_context:
        if user_ids is not None or team_ids is not None:
            raise ValueError("Cannot specify user_ids or team_ids when current_user_context is True.")
        user_context = users.build_user_context()
        user_ids = [user_context['user_id']]
        team_ids = user_context['team_ids']
    elif not (user_ids or team_ids):
            raise ValueError("Must specify at least user_ids or team_ids when current_user_context is False.")

    return escalation_policies.list_escalation_policies(
        query=query,
        user_ids=user_ids,
        team_ids=team_ids,
        limit=limit
    )

@server.tool()
def show_escalation_policy(*,
                          policy_id: str) -> Dict[str, Any]:
    """Show details about a given escalation policy.

    Args:
        policy_id (str): The ID of the escalation policy to show

    Returns:
        Dict[str, Any]: Escalation policy object with detailed information
    """
    return escalation_policies.show_escalation_policy(policy_id=policy_id)


"""
Incidents Tools
"""
@server.tool()
def list_incidents(*,
                   current_user_context: bool = True,
                   service_ids: Optional[List[str]] = None,
                   team_ids: Optional[List[str]] = None,
                   statuses: Optional[Union[List[str], str]] = None,
                   since: Optional[str] = None,
                   until: Optional[str] = None,
                   limit: Optional[int] = None) -> Dict[str, Any]:
    """List PagerDuty incidents based on specified filters.

    Args:
        current_user_context (bool): Boolean, use the current user's team_ids and service_ids to filter (default: True, cannot be used with service_ids or team_ids)
        service_ids (List[str]): list of PagerDuty service IDs to filter by (optional, cannot be used with current_user_context)
        team_ids (List[str]): list of PagerDuty team IDs to filter by (optional, cannot be used with current_user_context)
        statuses (List[str]): list of status values to filter by (optional). Valid values are:
            - 'triggered' - The incident is currently active (included by default)
            - 'acknowledged' - The incident has been acknowledged by a user (included by default)
            - 'resolved' - The incident has been resolved (excluded by default)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of incidents matching the specified criteria
    """
    if current_user_context:
        if service_ids is not None or team_ids is not None:
            raise ValueError("Cannot specify service_ids or team_ids when current_user_context is True.")
        user_context = users.build_user_context()
        team_ids = user_context['team_ids']
        service_ids = user_context['service_ids']
    elif not (service_ids or team_ids):
        raise ValueError("Must specify at least service_ids or team_ids when current_user_context is False.")

    if statuses is not None:
        if isinstance(statuses, str):
            statuses = [statuses.lower()]
        elif not isinstance(statuses, list):
            raise ValueError("statuses must be a list of strings or a single string.")

    return incidents.list_incidents(
        service_ids=service_ids,
        team_ids=team_ids,
        statuses=statuses,
        since=since,
        until=until,
        limit=limit
    )

@server.tool()
def show_incident(*,
                 incident_id: str) -> Dict[str, Any]:
    """Get detailed information about a given incident.

    Args:
        incident_id (str): The ID or number of the incident to get

    Returns:
        Dict[str, Any]: Incident object with detailed information
    """
    return incidents.show_incident(incident_id=incident_id)

@server.tool()
def list_past_incidents(*,
                       incident_id: str,
                       limit: Optional[int] = None,
                       total: Optional[bool] = None) -> Dict[str, Any]:
    """List incidents from the past 6 months that are similar to the input incident, and were generated on the same service as the parent incident. Results are ordered by similarity score.

    The returned incidents are in a slimmed down format containing only id, created_at, self, and title.
    Each incident also includes a similarity_score indicating how similar it is to the input incident.
    Incidents are sorted by similarity_score in descending order, so the most similar incidents appear first.

    Args:
        incident_id (str): The ID or number of the incident to find similar incidents for
        limit (int): The maximum number of past incidents to return (optional). Default in the API is 5.
        total (bool): Whether to return the total number of incidents that match the criteria (optional). Default is False.

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of similar incidents matching the specified criteria.
            Each incident in the list contains:
            - id (str): The incident ID
            - created_at (str): Creation timestamp
            - self (str): API URL for the incident
            - title (str): The incident title
            - similarity_score (float): Decimal value indicating similarity to the input incident
    """
    return incidents.list_past_incidents(
        incident_id=incident_id,
        limit=limit,
        total=total
    )

@server.tool()
def list_related_incidents(*,
                         incident_id: str) -> Dict[str, Any]:
    """List the 20 most recent related incidents that are impacting other services and responders.

    Args:
        incident_id (str): The ID or number of the incident to find related incidents for

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of related incidents matching the specified criteria.
            Each incident in the list contains:
            - id (str): The incident ID
            - summary (str): Summary of the incident
            - title (str): The incident title
            - status (str): Current status of the incident
            - urgency (str): Current urgency level of the incident
            - service (Dict): The service this incident belongs to
            - created_at (str): Creation timestamp
    """
    return incidents.list_related_incidents(incident_id=incident_id)

"""
Oncalls Tools
"""
@server.tool()
def list_oncalls(*,
                current_user_context: bool = True,
                schedule_ids: Optional[List[str]] = None,
                user_ids: Optional[List[str]] = None,
                escalation_policy_ids: Optional[List[str]] = None,
                since: Optional[str] = None,
                until: Optional[str] = None,
                limit: Optional[int] = None) -> Dict[str, Any]:
    """List the on-call entries during a given time range. An oncall-entry contains the user that is on-call for the given schedule, escalation policy, or time range and also includes the schedule and escalation policy that the user is on-call for.

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

    Args:
        current_user_context (bool): If True, shows on-calls for the current user's team's escalation policies. Cannot be used with user_ids. (default: True)
        schedule_ids (List[str]): Return only on-calls for the specified schedule IDs (optional)
        user_ids (List[str]): Return only on-calls for the specified user IDs (optional, cannot be used with current_user_context)
        escalation_policy_ids (List[str]): Return only on-calls for the specified escalation policy IDs (optional)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: A dictionary containing:
            - metadata (Dict[str, Any]): Contains result count and description
            - oncalls (List[Dict[str, Any]]): List of on-call entries, each containing:
                - user (Dict[str, Any]): The user who is on-call, including:
                    - id (str): User's PagerDuty ID
                    - summary (str): User's name
                    - html_url (str): URL to user's PagerDuty profile
                - escalation_policy (Dict[str, Any]): The policy this on-call is for, including:
                    - id (str): Policy's PagerDuty ID
                    - summary (str): Policy name
                    - html_url (str): URL to policy in PagerDuty
                - schedule (Dict[str, Any]): The schedule that generated this on-call, including:
                    - id (str): Schedule's PagerDuty ID
                    - summary (str): Schedule name
                    - html_url (str): URL to schedule in PagerDuty
                - escalation_level (int): The escalation level for this on-call
                - start (str): Start time of the on-call period in ISO8601 format
                - end (str): End time of the on-call period in ISO8601 format

    Example Response:
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
    """
    if current_user_context:
        if user_ids is not None:
            raise ValueError("Cannot specify user_ids when current_user_context is True.")
        user_context = users.build_user_context()
        escalation_policy_ids = user_context['escalation_policy_ids']
    elif not (schedule_ids or user_ids or escalation_policy_ids):
        raise ValueError("When current_user_context is False, must specify at least one of: schedule_ids, user_ids, or escalation_policy_ids")

    return oncalls.list_oncalls(
        user_ids=user_ids,
        schedule_ids=schedule_ids,
        escalation_policy_ids=escalation_policy_ids,
        since=since,
        until=until,
        limit=limit
    )

"""
Schedules Tools
"""
@server.tool()
def list_schedules(*,
                  query: Optional[str] = None,
                  limit: Optional[int] = None) -> Dict[str, Any]:
    """List the on-call schedules.

    Args:
        query (str): Filter schedules whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of schedules matching the specified criteria
    """
    return schedules.list_schedules(
        query=query,
        limit=limit
    )

@server.tool()
def show_schedule(*,
                schedule_id: str,
                since: Optional[str] = None,
                until: Optional[str] = None) -> Dict[str, Any]:
    """Show detailed information about a given schedule.

    Args:
        schedule_id (str): The ID of the schedule to get
        since (str): The start of the time range over which you want to search. Defaults to 2 weeks before until if an until is given. (optional)
        until (str): The end of the time range over which you want to search. Defaults to 2 weeks after since if a since is given. (optional)

    Returns:
        Dict[str, Any]: Schedule object with detailed information
    """
    return schedules.show_schedule(
        schedule_id=schedule_id,
        since=since,
        until=until
    )

@server.tool()
def list_users_oncall(*,
                     schedule_id: str,
                     since: Optional[str] = None,
                     until: Optional[str] = None) -> Dict[str, Any]:
    """List the users on call for a given schedule during the specified time range.

    Args:
        schedule_id (str): The ID of the schedule to list users on call for
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of users on call matching the specified criteria
    """
    return schedules.list_users_oncall(
        schedule_id=schedule_id,
        since=since,
        until=until
    )

"""
Services Tools
"""
@server.tool()
def list_services(*,
                  current_user_context: bool = True,
                  team_ids: Optional[List[str]] = None,
                  query: Optional[str] = None,
                  limit: Optional[int] = None) -> Dict[str, Any]:
    """List existing PagerDuty services.

    Args:
        current_user_context (bool): Use the current user's team IDs to filter (default: True, cannot be used with team_ids)
        team_ids (List[str]): Filter results to only services assigned to teams with the given IDs (optional, cannot be used with current_user_context)
        query (str): Filter services whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of services matching the specified criteria
    """
    if current_user_context:
        if team_ids is not None:
            raise ValueError("Cannot specify team_ids when current_user_context is True.")
        user_context = users.build_user_context()
        team_ids = user_context['team_ids']
    elif not team_ids:
        raise ValueError("Must specify at least team_ids when current_user_context is False.")

    return services.list_services(
        team_ids=team_ids,
        query=query,
        limit=limit
    )

@server.tool()
def show_service(*,
                service_id: str) -> Dict[str, Any]:
    """Get details about a given service.

    Args:
        service_id (str): The ID of the service to get

    Returns:
        Dict[str, Any]: Service object with detailed information
    """
    return services.show_service(service_id=service_id)


"""
Teams Tools
"""
@server.tool()
def list_teams(*,
               query: Optional[str] = None,
               limit: Optional[int] = None) -> Dict[str, Any]:
    """List teams in your PagerDuty account.

    Args:
        query (str): Filter teams whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of teams matching the specified criteria
    """
    return teams.list_teams(
        query=query,
        limit=limit
    )

@server.tool()
def show_team(*,
              team_id: str) -> Dict[str, Any]:
    """Get detailed information about a given team.

    Args:
        team_id (str): The ID of the team to get

    Returns:
        Dict[str, Any]: Team object with detailed information
    """
    return teams.show_team(team_id=team_id)


"""
Users Tools
"""
@server.tool()
def build_user_context() -> Dict[str, Any]:
    """Validate and build the current user's context into a dictionary with the following format:
        {
            "user_id": str,
            "team_ids": List[str],
            "service_ids": List[str],
            "escalation_policy_ids": List[str]
        }
    The MCP server tools use this user context to filter the following resources:
        - Escalation policies
        - Incidents
        - Oncalls
        - Services
        - Users

    Returns:
        Dict[str, Any]: Dictionary containing the current user's ID, team IDs, and service IDs.
            If the user context cannot be built (e.g., API errors or invalid user), returns a dictionary
            with empty strings for user_id and empty lists for all other fields.

    Raises:
        RuntimeError: If there are API errors while fetching user data
    """
    return users.build_user_context()

@server.tool()
def show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile including their teams, contact methods, and notification rules.

    Returns:
        Dict[str, Any]: The user object containing profile information in the following format (note this is non-exhaustive):
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "role": "user",
                "description": "John Doe is a user at Example Inc.",
                "job_title": "Software Engineer",
                "teams": [
                    {
                        "id": "P123456",
                        "summary": "Team Name 1"
                    },
                    ...
                ],
                "contact_methods": [
                    {
                        "id": "P123456",
                        "summary": "Mobile"
                    },
                    ...
                ],
                "notification_rules": [
                    {
                        "id": "P123456",
                        "summary": "0 minutes: channel XYZ"
                    },
                    ...
                ],
                "id": "P123456"
            }
    """
    return users.show_current_user()

@server.tool()
def list_users(*,
               current_user_context: bool = True,
               team_ids: Optional[List[str]] = None,
               query: Optional[str] = None,
               limit: Optional[int] = None) -> Dict[str, Any]:
    """List users in PagerDuty.

    Args:
        current_user_context (bool): Use the current user's team IDs to filter (default: True, cannot be used with team_ids)
        team_ids (List[str]): A list of team IDs to filter users (optional, cannot be used with current_user_context)
        query (str): A search query to filter users (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of users matching the specified criteria
    """
    if current_user_context:
        if team_ids is not None:
            raise ValueError("Cannot specify team_ids when current_user_context is True.")
        user_context = users.build_user_context()
        team_ids = user_context['team_ids']
    elif not team_ids:
        raise ValueError("Must specify at least team_ids when current_user_context is False.")

    return users.list_users(
        team_ids=team_ids,
        query=query,
        limit=limit
    )

@server.tool()
def show_user(*,
            user_id: str) -> Dict[str, Any]:
    """Get detailed information about a given user.

    Args:
        user_id (str): The ID of the user to get

    Returns:
        Dict[str, Any]: User object with detailed information
    """
    return users.show_user(user_id=user_id)
