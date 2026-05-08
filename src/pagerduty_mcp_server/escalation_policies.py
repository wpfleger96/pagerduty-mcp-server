"""PagerDuty escalation policy operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .async_utils import DEFAULT_MAX_RESULTS, paginate, safe_execute_async
from .client import create_client
from .models.escalation_policy import EscalationPolicy

logger = logging.getLogger(__name__)

ESCALATION_POLICIES_URL = "/escalation_policies"

"""
Escalation Policies API Helpers
"""


async def list_escalation_policies(
    *,
    query: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    team_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """List escalation policies based on the given criteria. Exposed in `get_escalation_policies`.

    Args:
        query (str): Filter escalation policies whose names contain the search query (optional)
        user_ids (List[str]): Filter results to only escalation policies that include the given user IDs (optional)
        team_ids (List[str]): Filter results to only escalation policies assigned to teams with the given IDs (optional)
        limit (int): Limit the number of results returned (optional)
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for each escalation policy

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of escalation policies in the standard format.
    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params = {}
    if query:
        params["query"] = query
    if user_ids:
        params["user_ids[]"] = user_ids
    if team_ids:
        params["team_ids[]"] = team_ids

    try:
        response = await paginate(
            pd_client,
            ESCALATION_POLICIES_URL,
            params=params,
            max_records=limit or DEFAULT_MAX_RESULTS,
            operation_name="list escalation policies",
        )
        return utils.parse_list_response(
            response, EscalationPolicy, "escalation_policies", include=include
        )
    except Exception as e:
        utils.handle_api_error(e)


async def show_escalation_policy(
    *, policy_id: str, include: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Get detailed information about a given escalation policy. Exposed in `get_escalation_policies`.

    Args:
        policy_id (str): The ID of the escalation policy to get
        include (List[str]): List of fields to include in the response. If specified, only these fields will be returned for the escalation policy

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single escalation policy in the standard format.
    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not policy_id:
        raise ValueError("policy_id cannot be empty")

    pd_client = create_client()

    try:
        response = await safe_execute_async(
            lambda: pd_client.jget(f"{ESCALATION_POLICIES_URL}/{policy_id}"),
            f"fetch escalation policy {policy_id}",
        )
        try:
            policy_data = response["escalation_policy"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch escalation policy {policy_id}: Response missing 'escalation_policy' field"
            )

        parsed_policy = {}
        if policy_data:
            model = EscalationPolicy.model_validate(policy_data)
            parsed_policy = model.to_clean_dict(include_fields=include)

        return utils.api_response_handler(
            results=parsed_policy,
            resource_name="escalation_policy",
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Escalation Policy Helpers
"""


async def fetch_escalation_policy_ids(*, user_id: Optional[str] = None) -> List[str]:
    """Get the escalation policy IDs for a user. Internal helper function.

    Args:
        user_id (str): The ID of the user

    Returns:
        List[str]: A list of escalation policy IDs associated with the user.
            Returns an empty list if no policies are found for the user.

    Note:
        This is an internal helper used by user-context building. It must
        return the COMPLETE set of policy IDs for the user — downstream
        filters (e.g. `get_oncalls(current_user_context=True)`) rely on
        having the full list. We therefore call `list_all` directly here
        instead of `list_escalation_policies`, which applies a tool-level
        result cap intended for caller-facing tools.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not user_id:
        raise ValueError("user_id cannot be empty")

    pd_client = create_client()
    params = {"user_ids[]": [user_id]}

    try:
        response = await safe_execute_async(
            lambda: pd_client.list_all(ESCALATION_POLICIES_URL, params=params),
            "fetch escalation policy IDs",
        )
        return [result["id"] for result in response if result and result.get("id")]
    except Exception as e:
        utils.handle_api_error(e)
