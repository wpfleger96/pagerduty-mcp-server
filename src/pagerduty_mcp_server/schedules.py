"""PagerDuty schedule operations."""

import logging
from typing import Any, Dict, Optional

from . import utils
from .client import create_client
from .parsers import parse_schedule, parse_user

logger = logging.getLogger(__name__)

SCHEDULES_URL = "/schedules"

"""
Schedules API Helpers
"""


def list_schedules(
    *, query: Optional[str] = None, limit: Optional[int] = None
) -> Dict[str, Any]:
    """List existing PagerDuty schedules. Returns all schedules that match the given search criteria. Exposed in `get_schedules`.

    Args:
        query (str): Filter schedules whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of schedules with their configuration and team assignments.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params = {}
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(SCHEDULES_URL, params=params)
        parsed_response = [parse_schedule(result=result) for result in response]
        return utils.api_response_handler(
            results=parsed_response, resource_name="schedules"
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_schedule(
    *, schedule_id: str, since: Optional[str] = None, until: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed information about a given schedule, including its configuration and current state. Exposed in `get_schedules`.

    Args:
        schedule_id (str): The ID of the schedule to get
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single schedule with detailed configuration and team information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not schedule_id:
        raise ValueError("schedule_id cannot be empty")

    pd_client = create_client()

    params = {}
    if since:
        utils.validate_iso8601_timestamp(since, "since")
        params["since"] = since
    if until:
        utils.validate_iso8601_timestamp(until, "until")
        params["until"] = until

    try:
        response = pd_client.jget(f"{SCHEDULES_URL}/{schedule_id}", params=params)
        try:
            schedule_data = response["schedule"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch schedule {schedule_id}: Response missing 'schedule' field"
            )

        return utils.api_response_handler(
            results=parse_schedule(result=schedule_data), resource_name="schedule"
        )
    except Exception as e:
        utils.handle_api_error(e)


def list_users_oncall(
    *, schedule_id: str, since: Optional[str] = None, until: Optional[str] = None
) -> Dict[str, Any]:
    """List the users on call for a given schedule during the specified time range. Returns a list of users who are or will be on call during the specified period. Exposed as MCP server tool.

    Args:
        schedule_id (str): The ID of the schedule to list users on call for
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of users who are on call during the specified time range.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not schedule_id:
        raise ValueError("schedule_id cannot be empty")

    pd_client = create_client()

    params = {}
    if since:
        utils.validate_iso8601_timestamp(since, "since")
        params["since"] = since
    if until:
        utils.validate_iso8601_timestamp(until, "until")
        params["until"] = until

    try:
        response = pd_client.jget(f"{SCHEDULES_URL}/{schedule_id}/users", params=params)
        try:
            users_data = response["users"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch users on call for schedule {schedule_id}: Response missing 'users' field"
            )

        return utils.api_response_handler(
            results=[parse_user(result=user) for user in users_data],
            resource_name="users",
        )
    except Exception as e:
        utils.handle_api_error(e)
