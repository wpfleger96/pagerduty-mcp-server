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
from . import utils

logger = logging.getLogger(__name__)
server = FastMCP("pagerduty_mcp_server")

"""
Escalation Policies Tools
"""
@server.tool()
def list_escalation_policies(*,
                            current_user_context: bool = True, 
                            query: Optional[str] = None,
                            user_ids: Optional[List[str]] = None,
                            team_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """List existing escalation policies based on the given criteria.
    
    Args:
        current_user_context (bool): Whether to use the current user's ID/team IDs context (default: True, cannot be used with user_ids or team_ids)
        query (str): Filter escalation policies whose names contain the search query (optional)
        user_ids (List[str]): Filter results to only escalation policies that include the given user IDs (optional, cannot be used with current_user_context)
        team_ids (List[str]): Filter results to only escalation policies assigned to teams with the given IDs (optional, cannot be used with current_user_context)
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of escalation policies matching the specified criteria
    """
    if current_user_context:
        if user_ids is not None or team_ids is not None:
            raise ValueError("Cannot specify user_ids or team_ids when current_user_context is True.")
        user_context = utils.build_user_context()
        user_ids = [user_context['user_id']]
        team_ids = user_context['team_ids']
    elif not (user_ids or team_ids):
            raise ValueError("Must specify at least user_ids or team_ids when current_user_context is False.")

    return escalation_policies.list_escalation_policies(
        query=query,
        user_ids=user_ids,
        team_ids=team_ids
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
                   until: Optional[str] = None) -> Dict[str, Any]:
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
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of incidents matching the specified criteria
    """
    if current_user_context:
        if service_ids is not None or team_ids is not None:
            raise ValueError("Cannot specify service_ids or team_ids when current_user_context is True.")
        user_context = utils.build_user_context()
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
        until=until
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
    """List past incidents similar to the input incident.

    Args:
        incident_id (str): The ID or number of the incident to find similar incidents for
        limit (int): The maximum number of past incidents to return (optional). Default in the API is 5.
        total (bool): Whether to return the total number of incidents that match the criteria (optional). Default is False.

    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of similar incidents matching the specified criteria
    """
    return incidents.list_past_incidents(
        incident_id=incident_id,
        limit=limit,
        total=total
    )

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
                until: Optional[str] = None) -> Dict[str, Any]:
    """List the on-call entries during a given time range.
    
    Args:
        current_user_context (bool): Use the current user's ID to filter (default: True, cannot be used with user_ids or escalation_policy_ids)
        schedule_ids (List[str]): Return only on-calls for the specified schedule IDs (optional)
        user_ids (List[str]): Return only on-calls for the specified user IDs (optional, cannot be used with current_user_context)
        escalation_policy_ids (List[str]): Return only on-calls for the specified escalation policy IDs (optional, cannot be used with current_user_context)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of on-call entries matching the specified criteria
    """
    if current_user_context:
        if user_ids is not None or escalation_policy_ids is not None:
            raise ValueError("Cannot specify user_ids or escalation_policy_ids when current_user_context is True.")
        user_context = utils.build_user_context()
        user_ids = [user_context['user_id']]
        escalation_policy_ids = user_context['escalation_policy_ids']
    elif not (user_ids or escalation_policy_ids):
        raise ValueError("Must specify at least user_ids or escalation_policy_ids when current_user_context is False.")

    return oncalls.list_oncalls(
        user_ids=user_ids,
        schedule_ids=schedule_ids,
        escalation_policy_ids=escalation_policy_ids,
        since=since,
        until=until
    )

"""
Schedules Tools
"""
@server.tool()
def list_schedules(*, 
                  query: Optional[str] = None) -> Dict[str, Any]:
    """List the on-call schedules.
    
    Args:
        query (str): Filter schedules whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of schedules matching the specified criteria
    """
    return schedules.list_schedules(query=query)

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

"""
Services Tools
"""
@server.tool()
def list_services(*,
                  current_user_context: bool = True,
                  team_ids: Optional[List[str]] = None,
                  query: Optional[str] = None) -> Dict[str, Any]:
    """List existing PagerDuty services.
    
    Args:
        current_user_context (bool): Use the current user's team IDs to filter (default: True, cannot be used with team_ids)
        team_ids (List[str]): Filter results to only services assigned to teams with the given IDs (optional, cannot be used with current_user_context)
        query (str): Filter services whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of services matching the specified criteria
    """
    if current_user_context:
        if team_ids is not None:
            raise ValueError("Cannot specify team_ids when current_user_context is True.")
        user_context = utils.build_user_context()
        team_ids = user_context['team_ids']
    elif not team_ids:
        raise ValueError("Must specify at least team_ids when current_user_context is False.")

    return services.list_services(
        team_ids=team_ids,
        query=query
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
               query: Optional[str] = None) -> Dict[str, Any]:
    """List teams in your PagerDuty account.
    
    Args:
        query (str): Filter teams whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of teams matching the specified criteria
    """
    return teams.list_teams(query=query)

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
               query: Optional[str] = None) -> Dict[str, Any]:
    """List users in PagerDuty.

    Args:
        current_user_context (bool): Use the current user's team IDs to filter (default: True, cannot be used with team_ids)
        team_ids (List[str]): A list of team IDs to filter users (optional, cannot be used with current_user_context)
        query (str): A search query to filter users (optional)
    
    Returns:
        Dict[str, Any]: Dictionary containing metadata (count, description) and a list of users matching the specified criteria
    """
    if current_user_context:
        if team_ids is not None:
            raise ValueError("Cannot specify team_ids when current_user_context is True.")
        user_context = utils.build_user_context()
        team_ids = user_context['team_ids']
    elif not team_ids:
        raise ValueError("Must specify at least team_ids when current_user_context is False.")

    return users.list_users(
        team_ids=team_ids,
        query=query
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
