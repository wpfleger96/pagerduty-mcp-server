"""PagerDuty MCP Server main module."""

from functools import wraps
from importlib.metadata import version
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from . import (
    escalation_policies,
    incidents,
    oncalls,
    schedules,
    services,
    teams,
    users,
    utils,
    validation,
)
from .models.escalation_policy import EscalationPolicy
from .models.incident import Incident
from .models.oncall import Oncall
from .models.schedule import Schedule
from .models.service import Service
from .models.team import Team
from .models.user import User

instructions = f"""
PagerDuty MCP Server v{version("pagerduty_mcp_server")}

REQUIRED READING: You MUST read all tool documentation using the resource `docs://tools` before using any tools. Failure to read the tools documentation may result in incorrect or incomplete results.
"""

mcp = FastMCP(
    name="pagerduty_mcp_server",
    instructions=instructions,
)


def tool_error_boundary(
    func: Callable[..., Awaitable[Dict[str, Any]]],
) -> Callable[..., Awaitable[Dict[str, Any]]]:
    """Convert common tool failures into ToolError so FastMCP sets isError=true."""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return await func(*args, **kwargs)
        except ToolError:
            raise
        except Exception as exc:
            response = getattr(exc, "response", None)
            if response is not None:
                message = response.text
            else:
                message = str(exc)
            raise ToolError(message) from exc

    return wrapper


"""
Tool Documentation
"""


@mcp.resource("docs://tools")
def get_tool_documentation() -> str:
    with open(str(Path(__file__).resolve().parent / "docs/tools.md"), "r") as f:
        return f.read()


"""
Escalation Policies Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(EscalationPolicy)
async def get_escalation_policies(
    *,
    policy_id: Optional[str] = None,
    current_user_context: bool = True,
    query: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    team_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty escalation policies by filters or get details for a specific policy ID.

    Args:
        policy_id (str): The escalation policy ID to retrieve (optional, cannot be used with any other filters).
        current_user_context (bool): Use current user's ID/team IDs context (default: True). Not used if `policy_id` is provided.
        query (str): Policies whose names contain the search query (optional). Not used if `policy_id` is provided.
        user_ids (List[str]): Policies that include these user IDs (optional, excludes current_user_context). Not used if `policy_id` is provided.
        team_ids (List[str]): Policies assigned to these team IDs (optional, excludes current_user_context). Not used if `policy_id` is provided.
        limit (int): Limit the number of results (optional). Not used if `policy_id` is provided.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each escalation policy
    """
    if policy_id is not None:
        disallowed_filters_present = (
            query is not None
            or user_ids is not None
            or team_ids is not None
            or limit is not None
        )
        if disallowed_filters_present:
            raise ValueError(
                "When `policy_id` is provided, other filters (like query, user_ids, team_ids, limit) cannot be used. See `docs://tools` for more information."
            )

        return await escalation_policies.show_escalation_policy(
            policy_id=policy_id, include=include
        )

    if current_user_context:
        if user_ids is not None or team_ids is not None:
            raise ValueError(
                "Cannot specify user_ids or team_ids when current_user_context is True. See `docs://tools` for more information."
            )
        user_context = await users.build_user_context()
        user_ids = [user_context["user_id"]]
        team_ids = user_context["team_ids"]
    elif not (user_ids or team_ids):
        raise ValueError(
            "Must specify at least user_ids or team_ids when current_user_context is False. See `docs://tools` for more information."
        )

    return await escalation_policies.list_escalation_policies(
        query=query,
        user_ids=user_ids,
        team_ids=team_ids,
        limit=limit,
        include=include,
    )


"""
Incidents Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(
    Incident, extra_fields=["notes", "past_incidents", "related_incidents"]
)
async def get_incidents(
    *,
    incident_id: Optional[str] = None,
    current_user_context: bool = True,
    service_ids: Optional[List[str]] = None,
    team_ids: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    urgencies: Optional[List[str]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: Optional[int] = None,
    include_past_incidents: Optional[bool] = False,
    include_related_incidents: Optional[bool] = False,
    include_notes: Optional[bool] = False,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty incidents by filters or get details for a specific incident ID or number.

    Args:
        incident_id (str): The incident ID or number to retrieve (optional, cannot be used with any other filters).
        current_user_context (bool): Filter by current user's context (default: True). Not used if `incident_id` is provided.
        service_ids (List[str]): Filter by services (optional, excludes current_user_context). Not used if `incident_id` is provided.
        team_ids (List[str]): Filter by teams (optional, excludes current_user_context). Not used if `incident_id` is provided.
        statuses (List[str]): Filter by status (optional). Not used if `incident_id` is provided. Must be input as a list of strings, valid values are `["triggered", "acknowledged", "resolved"]`. Defaults to all statuses.
        urgencies (List[str]): Filter by urgency (optional). Not used if `incident_id` is provided. Must be input as a list of strings, valid values are `["high", "low"]`. Defaults to all urgencies. Account must have the urgencies ability to do this.
        since (str): Start of query range in ISO8601 format (default range: 1 month, max range: 6 months). Not used if `incident_id` is provided.
        until (str): End of query range in ISO8601 format (default range: 1 month, max range: 6 months). Not used if `incident_id` is provided.
        limit (int): Max results (optional). Not used if `incident_id` is provided.
        include_past_incidents (Optional[bool]): If True and `incident_id` is provided, includes similar past incidents in the response. Defaults to False. Cannot be used without `incident_id`.
        include_related_incidents (Optional[bool]): If True and `incident_id` is provided, includes related incidents impacting other services/responders in the response. Defaults to False. Cannot be used without `incident_id`.
        include_notes (Optional[bool]): If True, includes notes for each incident in the response. Defaults to False.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each incident
    """
    if incident_id is not None:
        disallowed_filters_present = (
            service_ids is not None
            or team_ids is not None
            or statuses is not None
            or since is not None
            or until is not None
            or limit is not None
        )
        if disallowed_filters_present:
            raise ValueError(
                "When `incident_id` is provided, other filters (like service_ids, team_ids, statuses, etc.) cannot be used. See `docs://tools` for more information."
            )

        incident_response = await incidents.show_incident(
            incident_id=incident_id,
            include_past_incidents=include_past_incidents,
            include_related_incidents=include_related_incidents,
            include_notes=include_notes,
            include=include,
        )

        return incident_response

    if include_past_incidents or include_related_incidents or include_notes:
        raise ValueError(
            "`include_past_incidents`, `include_related_incidents`, and `include_notes` can only be used when a specific `incident_id` is provided. See `docs://tools` for more information."
        )

    if current_user_context:
        if service_ids is not None or team_ids is not None:
            raise ValueError(
                "Cannot specify service_ids or team_ids when current_user_context is True. See `docs://tools` for more information."
            )
        user_context = await users.build_user_context()
        team_ids = user_context["team_ids"]
        service_ids = user_context["service_ids"]
    elif not (service_ids or team_ids):
        raise ValueError(
            "Must specify at least service_ids or team_ids when current_user_context is False. See `docs://tools` for more information."
        )

    if since and until:
        utils.validate_timestamp_range(since, until)

    incidents_response = await incidents.list_incidents(
        service_ids=service_ids,
        team_ids=team_ids,
        statuses=statuses,
        urgencies=urgencies,
        since=since,
        until=until,
        limit=limit,
        include=include,
    )

    return incidents_response


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Incident)
async def acknowledge_incident(
    *,
    incident_id: str,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Acknowledge a PagerDuty incident. This signals that someone is actively working on the incident.

    Args:
        incident_id (str): The ID of the incident to acknowledge (required).
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for the incident.
    """
    return await incidents.update_incident_status(
        incident_id=incident_id,
        status="acknowledged",
        include=include,
    )


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Incident)
async def resolve_incident(
    *,
    incident_id: str,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Resolve a PagerDuty incident. This marks the incident as resolved and stops any further escalations.

    Args:
        incident_id (str): The ID of the incident to resolve (required).
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for the incident.
    """
    return await incidents.update_incident_status(
        incident_id=incident_id,
        status="resolved",
        include=include,
    )


@mcp.tool()
@tool_error_boundary
async def add_incident_note(
    *,
    incident_id: str,
    content: str,
) -> Dict[str, Any]:
    """Add a note to a PagerDuty incident. Notes are used to record additional context, investigation progress, or resolution details.

    Args:
        incident_id (str): The ID of the incident to add a note to (required).
        content (str): The text content of the note (required).
    """
    return await incidents.create_incident_note(
        incident_id=incident_id,
        content=content,
    )


"""
Oncalls Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Oncall)
async def get_oncalls(
    *,
    current_user_context: bool = True,
    schedule_ids: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    escalation_policy_ids: Optional[List[str]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: Optional[int] = None,
    earliest: Optional[bool] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """List on-call entries for schedules, policies, or time ranges.

    Behavior varies by time parameters:
    1. Without since/until: Returns current on-calls
       Example: get_oncalls(schedule_ids=["SCHEDULE_123"])
    2. With since/until: Returns all on-calls in range
       Example: get_oncalls(schedule_ids=["SCHEDULE_123"], since="2024-03-20T00:00:00Z", until="2024-03-27T00:00:00Z")

    Args:
        current_user_context (bool): Use current user's team policies (default: True)
        schedule_ids (List[str]): Filter by schedules (optional)
        user_ids (List[str]): Filter by users (optional, excludes current_user_context)
        escalation_policy_ids (List[str]): Filter by policies (optional)
        since (str): Start of query range in ISO8601 format (default: current datetime)
        until (str): End of query range in ISO8601 format (default: current datetime, max range: 90 days in the future). Cannot be before `since`.
        limit (int): Max results (optional)
        earliest (bool): Only earliest on-call per policy/level/user combo (optional)
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each on-call entry
    """
    if current_user_context:
        if user_ids is not None:
            raise ValueError(
                "Cannot specify user_ids when current_user_context is True. See `docs://tools` for more information."
            )
        user_context = await users.build_user_context()
        escalation_policy_ids = user_context["escalation_policy_ids"]
    elif not (schedule_ids or user_ids or escalation_policy_ids):
        raise ValueError(
            "When current_user_context is False, must specify at least one of: schedule_ids, user_ids, or escalation_policy_ids. See `docs://tools` for more information."
        )

    if since and until:
        utils.validate_timestamp_range(since, until)

    return await oncalls.list_oncalls(
        user_ids=user_ids,
        schedule_ids=schedule_ids,
        escalation_policy_ids=escalation_policy_ids,
        since=since,
        until=until,
        limit=limit,
        earliest=earliest,
        include=include,
    )


"""
Schedules Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Schedule)
async def get_schedules(
    *,
    schedule_id: Optional[str] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty schedules by filters or get details for a specific schedule ID.

    Args:
        schedule_id (str): The schedule ID to retrieve details for (optional, cannot be used with query or limit).
        query (str): Filter schedules whose names contain the search query (optional). Not used if `schedule_id` is provided.
        limit (int): Limit the number of results returned (optional). Not used if `schedule_id` is provided.
        since (str): Start time for overrides/final schedule details (ISO8601, optional). Only used if `schedule_id` is provided. Defaults to 2 weeks before 'until' if 'until' is given.
        until (str): End time for overrides/final schedule details (ISO8601, optional). Only used if `schedule_id` is provided. Defaults to 2 weeks after 'since' if 'since' is given.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each schedule
    """
    if schedule_id is not None:
        if query is not None or limit is not None:
            raise ValueError(
                "When `schedule_id` is provided, other filters (query, limit) cannot be used. See `docs://tools` for more information."
            )

        if since and until:
            utils.validate_timestamp_range(since, until)

        return await schedules.show_schedule(
            schedule_id=schedule_id, since=since, until=until, include=include
        )
    else:
        return await schedules.list_schedules(query=query, limit=limit, include=include)


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(User)
async def list_users_oncall(
    *,
    schedule_id: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """List the users on call for a schedule during the specified time range.

    Args:
        schedule_id (str): The ID of the schedule to query
        since (str): Start of query range in ISO8601 format
        until (str): End of query range in ISO8601 format
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each user on call
    """
    if since and until:
        utils.validate_timestamp_range(since, until)

    return await schedules.list_users_oncall(
        schedule_id=schedule_id, since=since, until=until, include=include
    )


"""
Services Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Service)
async def get_services(
    *,
    service_id: Optional[str] = None,
    current_user_context: bool = True,
    team_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty services by filters or get details for a specific service ID.

    Args:
        service_id (str): The service ID to retrieve (optional, cannot be used with any other filters).
        current_user_context (bool): Use current user's team IDs to filter (default: True). Not used if `service_id` is provided.
        team_ids (List[str]): Filter results to only services assigned to teams with the given IDs (optional, cannot be used with current_user_context). Not used if `service_id` is provided.
        query (str): Filter services whose names contain the search query (optional). Not used if `service_id` is provided.
        limit (int): Limit the number of results (optional). Not used if `service_id` is provided.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each service
    """
    if service_id is not None:
        disallowed_filters_present = (
            team_ids is not None or query is not None or limit is not None
        )
        if disallowed_filters_present:
            raise ValueError(
                "When `service_id` is provided, other filters (like team_ids, query, limit) cannot be used. See `docs://tools` for more information."
            )

        return await services.show_service(service_id=service_id, include=include)

    if current_user_context:
        if team_ids is not None:
            raise ValueError(
                "Cannot specify team_ids when current_user_context is True. See `docs://tools` for more information."
            )
        user_context = await users.build_user_context()
        team_ids = user_context["team_ids"]
    elif not team_ids:
        raise ValueError(
            "Must specify at least team_ids when current_user_context is False. See `docs://tools` for more information."
        )

    return await services.list_services(
        team_ids=team_ids, query=query, limit=limit, include=include
    )


"""
Teams Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(Team)
async def get_teams(
    *,
    team_id: Optional[str] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty teams by filters or get details for a specific team ID.

    Args:
        team_id (str): The team ID to retrieve (optional, cannot be used with any other filters).
        query (str): Filter teams whose names contain the search query (optional). Not used if `team_id` is provided.
        limit (int): Limit the number of results returned (optional). Not used if `team_id` is provided.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each team
    """
    if team_id is not None:
        disallowed_filters_present = query is not None or limit is not None
        if disallowed_filters_present:
            raise ValueError(
                "When `team_id` is provided, other filters (like query, limit) cannot be used. See `docs://tools` for more information."
            )

        return await teams.show_team(team_id=team_id, include=include)

    return await teams.list_teams(query=query, limit=limit, include=include)


"""
Users Tools
"""


@mcp.tool()
@tool_error_boundary
@validation.validate_include_parameter(User)
async def get_users(
    *,
    user_id: Optional[str] = None,
    current_user_context: bool = True,
    team_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Get PagerDuty users by filters or get details for a specific user ID.

    Args:
        user_id (str): The user ID to retrieve (optional, cannot be used with any other filters).
        current_user_context (bool): Use current user's team IDs to filter (default: True). Not used if `user_id` is provided.
        team_ids (List[str]): Filter results to only users assigned to teams with the given IDs (optional, cannot be used with current_user_context). Not used if `user_id` is provided.
        query (str): Filter users whose names contain the search query (optional). Not used if `user_id` is provided.
        limit (int): Limit the number of results (optional). Not used if `user_id` is provided.
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each user
    """
    if user_id is not None:
        disallowed_filters_present = (
            team_ids is not None or query is not None or limit is not None
        )
        if disallowed_filters_present:
            raise ValueError(
                "When `user_id` is provided, other filters (like team_ids, query, limit) cannot be used. See `docs://tools` for more information."
            )

        return await users.show_user(user_id=user_id, include=include)

    if current_user_context:
        if team_ids is not None:
            raise ValueError(
                "Cannot specify team_ids when current_user_context is True. See `docs://tools` for more information."
            )
        user_context = await users.build_user_context()
        team_ids = user_context["team_ids"]
    elif not team_ids:
        raise ValueError(
            "Must specify at least team_ids when current_user_context is False. See `docs://tools` for more information."
        )

    return await users.list_users(
        team_ids=team_ids, query=query, limit=limit, include=include
    )


@mcp.tool()
@tool_error_boundary
async def build_user_context() -> Dict[str, Any]:
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
    """
    return await users.build_user_context()
