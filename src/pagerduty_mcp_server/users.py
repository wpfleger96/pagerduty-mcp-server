"""PagerDuty user operations."""

import logging
from typing import Any, Dict, List, Optional

from . import escalation_policies, services, teams, utils
from .client import create_client
from .parsers import parse_user

USERS_URL = "/users"

logger = logging.getLogger(__name__)


def build_user_context() -> Dict[str, Any]:
    """Validate and build the current user's context. Exposed as MCP server tool.

    See the "Standard Response Format" section in `tools.md` for the complete standard response structure.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain the current user's context in the format defined in the "build_user_context" section of `tools.md`.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """
    try:
        user = _show_current_user()
        if not user:
            raise ValueError("Failed to get current user data")

        context = {
            "user_id": str(user.get("id", "")).strip(),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "team_ids": [],
            "service_ids": [],
            "escalation_policy_ids": [],
        }

        if not context["user_id"]:
            raise ValueError("Invalid user data: missing or empty user ID")

        team_ids = teams.fetch_team_ids(user=user)
        context["team_ids"] = [
            str(tid).strip() for tid in team_ids if tid and str(tid).strip()
        ]

        if context["team_ids"]:
            service_ids = services.fetch_service_ids(team_ids=context["team_ids"])
            context["service_ids"] = [
                str(sid).strip() for sid in service_ids if sid and str(sid).strip()
            ]

        escalation_policy_ids = escalation_policies.fetch_escalation_policy_ids(
            user_id=context["user_id"]
        )
        context["escalation_policy_ids"] = [
            str(epid).strip()
            for epid in escalation_policy_ids
            if epid and str(epid).strip()
        ]

        return context

    except Exception as e:
        utils.handle_api_error(e)


"""
Users API Helpers
"""


def list_users(
    *,
    team_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """List users in PagerDuty. Exposed as MCP server tool.

    Args:
        team_ids (List[str]): Filter results to only users assigned to teams with the given IDs (optional)
        query (str): Filter users whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of users with their profile information including teams, contact methods, and notification rules.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params = {}

    if team_ids:
        params["team_ids[]"] = team_ids
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(USERS_URL, params=params)
        parsed_response = [parse_user(result=result) for result in response]
        return utils.api_response_handler(
            results=parsed_response, resource_name="users"
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_user(*, user_id: str) -> Dict[str, Any]:
    """Get detailed information about a given user. Exposed as MCP server tool.

    Args:
        user_id (str): The ID of the user to fetch

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single user with detailed profile information including teams, contact methods, and notification rules.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not user_id:
        raise ValueError("User ID is required")

    pd_client = create_client()

    try:
        response = pd_client.jget(f"{USERS_URL}/{user_id}")
        try:
            user_data = response["user"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch user {user_id}: Response missing 'user' field"
            )

        return utils.api_response_handler(
            results=parse_user(result=user_data), resource_name="user"
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Users Private Helpers
"""


def _show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile including their teams, contact methods, and notification rules.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single user with detailed profile information including teams, contact methods, and notification rules.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """
    pd_client = create_client()
    try:
        response = pd_client.jget(USERS_URL + "/me")["user"]
        user = parse_user(result=response)
        if not user or "id" not in user or not user["id"]:
            raise ValueError("Invalid user object: missing ID")
        return user
    except Exception as e:
        utils.handle_api_error(e)
