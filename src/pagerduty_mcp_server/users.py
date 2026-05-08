"""PagerDuty user operations."""

import logging
from typing import Any, Dict, List, Optional

from . import escalation_policies, services, teams, utils
from .async_utils import DEFAULT_MAX_RESULTS, paginate, safe_execute_async
from .client import create_client
from .models.user import User

USERS_URL = "/users"

logger = logging.getLogger(__name__)


async def build_user_context() -> Dict[str, Any]:
    """Validate and build the current user's context. Exposed as MCP server tool.

    See the "Standard Response Format" section in `tools.md` for the complete standard response structure.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain the current user's context in the format defined in the "build_user_context" section of `tools.md`.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """
    try:
        user = await _show_current_user()
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
            service_ids = await services.fetch_service_ids(team_ids=context["team_ids"])
            context["service_ids"] = [
                str(sid).strip() for sid in service_ids if sid and str(sid).strip()
            ]

        escalation_policy_ids = await escalation_policies.fetch_escalation_policy_ids(
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


async def list_users(
    *,
    team_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """List users in PagerDuty. Exposed as MCP server tool.

    Args:
        team_ids (List[str]): Filter results to only users assigned to teams with the given IDs (optional)
        query (str): Filter users whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each user

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of users with their profile information including teams, contact methods, and notification rules.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params: Dict[str, Any] = {}

    if team_ids:
        params["team_ids[]"] = team_ids
    if query:
        params["query"] = query

    try:
        response = await paginate(
            pd_client,
            USERS_URL,
            params=params,
            max_records=limit or DEFAULT_MAX_RESULTS,
            operation_name="list users",
        )
        return utils.parse_list_response(response, User, "users", include=include)
    except Exception as e:
        utils.handle_api_error(e)


async def show_user(
    *, user_id: str, include: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get detailed information about a given user. Exposed as MCP server tool.

    Args:
        user_id (str): The ID of the user to fetch
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for the user

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
        response = await safe_execute_async(
            lambda: pd_client.jget(f"{USERS_URL}/{user_id}"), f"fetch user {user_id}"
        )
        try:
            user_data = response["user"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch user {user_id}: Response missing 'user' field"
            )

        parsed_user = {}
        if user_data:
            model = User.model_validate(user_data)
            parsed_user = model.to_clean_dict(include_fields=include)

        return utils.api_response_handler(results=parsed_user, resource_name="user")
    except Exception as e:
        utils.handle_api_error(e)


"""
Users Private Helpers
"""


async def _show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile including their teams, contact methods, and notification rules.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single user with detailed profile information including teams, contact methods, and notification rules.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """
    pd_client = create_client()
    try:
        result = await safe_execute_async(
            lambda: pd_client.jget(USERS_URL + "/me"), "fetch current user"
        )
        response = result["user"]
        user = {}
        if response:
            model = User.model_validate(response)
            user = model.to_clean_dict()
        if not user or "id" not in user or not user["id"]:
            raise ValueError("Invalid user object: missing ID")
        return user
    except Exception as e:
        utils.handle_api_error(e)
