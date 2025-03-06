"""PagerDuty MCP Server main module."""

import asyncio
import logging
import logging.handlers
import os
import sys
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP
import pagerduty

from . import escalation_policies
from . import incidents
from . import oncall
from . import schedules
from . import services
from . import teams
from . import users

os.makedirs('./log', exist_ok=True)

# Configure log rotation - 1MB files, keep 50 backups
file_handler = logging.handlers.RotatingFileHandler(
    filename='./log/pagerduty-mcp-server.log',
    maxBytes=1024*1024,  # 1MB
    backupCount=50
)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger("pagerduty-mcp-server")

server = FastMCP("pagerduty_mcp_server")


"""
Escalation Policies Tools
"""
@server.tool()
def list_escalation_policies(*, 
                           query: Optional[str] = None,
                           user_ids: List[str] = None,
                           team_ids: List[str] = None,
                           include: List[str] = None,
                           sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """List existing escalation policies.
    
    Args:
        query: Filter escalation policies whose names contain the search query
        user_ids: Filter results to only escalation policies that include the given user IDs
        team_ids: Filter results to only escalation policies assigned to teams with the given IDs
        include: Array of additional details to include. Options: teams,services,num_loops,current_state
        sort_by: Sort result by the given field. Options: name,description
    
    Returns:
        List[Dict[str, Any]]: List of escalation policy objects matching the specified criteria
    """
    return escalation_policies.list_escalation_policies(
        query=query,
        user_ids=user_ids,
        team_ids=team_ids,
        include=include,
        sort_by=sort_by
    )

@server.tool()
def get_escalation_policy(policy_id: str, *,
                         include: List[str] = None) -> Dict[str, Any]:
    """Show details about a given escalation policy.
    
    Args:
        policy_id: The ID of the escalation policy to get
        include: Array of additional details to include. Options: teams,services,num_loops,current_state
    
    Returns:
        Dict[str, Any]: Escalation policy object with detailed information
    """
    return escalation_policies.get_escalation_policy(policy_id, include=include)


"""
Incidents Tools
"""
@server.tool()
def list_incidents(*, 
                  service_ids: List[str] = None, 
                  team_ids: List[str] = None, 
                  statuses: List[str] = None, 
                  use_my_teams: bool = True,
                  date_range: Optional[str] = None,
                  since: Optional[str] = None,
                  until: Optional[str] = None) -> List[Dict[str, Any]]:
    """List PagerDuty incidents based on specified filters.
    
    Provides a flexible interface for querying PagerDuty incidents with support
    for filtering by teams, services, status, and date ranges. When use_my_teams
    is True (default), automatically uses the current user's team context.
    
    Args:
        service_ids: Optional list of service IDs to filter by
        team_ids: Optional list of team IDs to filter by
        statuses: Optional list of status values to filter by
        use_my_teams: Whether to use the current user's teams/services context (default: True)
        date_range: When set to "all", the since and until parameters are ignored
        since: Start of date range (ISO8601 format). Default is 1 month ago
        until: End of date range (ISO8601 format). Default is now
    
    Returns:
        List[Dict[str, Any]]: List of incident objects matching the specified criteria
    
    Raises:
        ValueError: If the parameter combination is invalid or if status values are invalid
    """
    return incidents.list_incidents(
        service_ids=service_ids,
        team_ids=team_ids,
        statuses=statuses,
        use_my_teams=use_my_teams,
        date_range=date_range,
        since=since,
        until=until
    )

@server.tool()
def get_incident(*,
                 id: Union[str, int]) -> Dict[str, Any]:
    """Get detailed information about a given incident.
    
    Args:
        id: The ID or number of the incident to get
    
    Returns:
        Dict[str, Any]: Incident object with detailed information
    """
    return incidents.get_incident(id=id)


"""
Oncalls Tools
"""
@server.tool()
def list_oncall(*, 
                schedule_ids: List[str] = None,
                user_ids: List[str] = None,
                escalation_policy_ids: List[str] = None,
                since: Optional[str] = None,
                until: Optional[str] = None,
                include: List[str] = None) -> List[Dict[str, Any]]:
    """List the on-call entries during a given time range.
    
    Args:
        schedule_ids: Return only on-calls for the specified schedule IDs
        user_ids: Return only on-calls for the specified user IDs
        escalation_policy_ids: Return only on-calls for the specified escalation policy IDs
        since: The start of the time range over which you want to search
        until: The end of the time range over which you want to search
        include: Array of additional details to include. Options: users,schedules,escalation_policies
    
    Returns:
        List[Dict[str, Any]]: List of on-call entries matching the specified criteria
    """
    return oncall.list_oncall(
        schedule_ids=schedule_ids,
        user_ids=user_ids,
        escalation_policy_ids=escalation_policy_ids,
        since=since,
        until=until,
        include=include
    )

"""
Schedules Tools
"""
@server.tool()
def list_schedules(*, 
                  query: Optional[str] = None,
                  include: List[str] = None) -> List[Dict[str, Any]]:
    """List the on-call schedules.
    
    Args:
        query: Filter schedules whose names contain the search query
        include: Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers
    
    Returns:
        List[Dict[str, Any]]: List of schedule objects
    """
    return schedules.list_schedules(query=query, include=include)

@server.tool()
def get_schedule(schedule_id: str, *,
                since: Optional[str] = None,
                until: Optional[str] = None,
                include: List[str] = None) -> Dict[str, Any]:
    """Show detailed information about a given schedule.
    
    Args:
        schedule_id: The ID of the schedule to get
        since: The start of the time range over which you want to search
        until: The end of the time range over which you want to search
        include: Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers
    
    Returns:
        Dict[str, Any]: Schedule object with detailed information
    """
    return schedules.get_schedule(
        schedule_id,
        since=since,
        until=until,
        include=include
    )


"""
Services Tools
"""
@server.tool()
def list_services(*, 
                 team_ids: List[str] = None,
                 include: List[str] = None,
                 query: Optional[str] = None,
                 time_zone: Optional[str] = None,
                 sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """List existing PagerDuty services.
    
    Args:
        team_ids: Filter results to only services assigned to teams with the given IDs
        include: Array of additional details to include. Options: escalation_policy,teams
        query: Filter services whose names contain the search query
        time_zone: Time zone in which dates should be rendered
        sort_by: Sort result by the given field. Options: name,status,created_at
    
    Returns:
        List[Dict[str, Any]]: List of service objects matching the specified criteria
    """
    return services.list_services(
        team_ids=team_ids,
        include=include,
        query=query,
        time_zone=time_zone,
        sort_by=sort_by
    )


@server.tool()
def get_service(service_id: str, *,
                include: List[str] = None) -> Dict[str, Any]:
    """Get details about a given service.
    
    Args:
        service_id: The ID of the service to get
        include: Array of additional details to include. Options: escalation_policy,teams
    
    Returns:
        Dict[str, Any]: Service object with detailed information
    """
    return services.get_service(service_id, include=include)


"""
Teams Tools
"""
@server.tool()
def list_teams(*, 
               query: Optional[str] = None,
               include: List[str] = None) -> List[Dict[str, Any]]:
    """List teams in your PagerDuty account.
    
    Args:
        query: Filter teams whose names contain the search query
        include: Array of additional details to include. Options: members,notification_rules
    
    Returns:
        List[Dict[str, Any]]: List of team objects matching the specified criteria
    """
    return teams.list_teams(query=query, include=include)

@server.tool()
def get_team(team_id: str, *,
             include: List[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given team.
    
    Args:
        team_id: The ID of the team to get
        include: Array of additional details to include. Options: members,notification_rules
    
    Returns:
        Dict[str, Any]: Team object with detailed information
    """
    return teams.get_team(team_id, include=include)


"""
Users Tools
"""
@server.tool()
def show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile.
    
    Returns:
        Dict[str, Any]: The user object containing profile information
    """
    return users.show_current_user()

@server.tool()
def get_user_context() -> tuple[List[str], List[str]]:
    """Get the current user's teams and associated services.
    
    Fetches the user's team memberships and then queries for all services
    associated with those teams.

    Returns:
        tuple[List[str], List[str]]: A tuple of (team_ids, service_ids)
    """
    return users.get_user_context()
