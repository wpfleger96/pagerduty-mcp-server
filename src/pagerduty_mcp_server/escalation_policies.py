"""PagerDuty escalation policy operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .client import create_client
from .parsers import parse_escalation_policy

logger = logging.getLogger(__name__)

ESCALATION_POLICIES_URL = "/escalation_policies"

"""
Escalation Policies API Helpers
"""


def list_escalation_policies(
    *,
    query: Optional[str] = None,
    user_ids: Optional[List[str]] = None,
    team_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """List escalation policies based on the given criteria. Exposed in `get_escalation_policies`.

    Args:
        query (str): Filter escalation policies whose names contain the search query (optional)
        user_ids (List[str]): Filter results to only escalation policies that include the given user IDs (optional)
        team_ids (List[str]): Filter results to only escalation policies assigned to teams with the given IDs (optional)
        limit (int): Limit the number of results returned (optional)

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
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(ESCALATION_POLICIES_URL, params=params)
        parsed_response = [
            parse_escalation_policy(result=result) for result in response
        ]
        return utils.api_response_handler(
            results=parsed_response, resource_name="escalation_policies"
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_escalation_policy(*, policy_id: str) -> Dict[str, Any]:
    """Get detailed information about a given escalation policy. Exposed in `get_escalation_policies`.

    Args:
        policy_id (str): The ID of the escalation policy to get

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
        response = pd_client.jget(f"{ESCALATION_POLICIES_URL}/{policy_id}")
        try:
            policy_data = response["escalation_policy"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch escalation policy {policy_id}: Response missing 'escalation_policy' field"
            )

        return utils.api_response_handler(
            results=parse_escalation_policy(result=policy_data),
            resource_name="escalation_policy",
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Escalation Policy Helpers
"""


def fetch_escalation_policy_ids(*, user_id: Optional[str] = None) -> List[str]:
    """Get the escalation policy IDs for a user. Internal helper function.

    Args:
        user_id (str): The ID of the user

    Returns:
        List[str]: A list of escalation policy IDs associated with the user.
            Returns an empty list if no policies are found for the user.

    Note:
        This is an internal helper function used by other modules to fetch escalation policy IDs.
        It should not be called directly by external code.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not user_id:
        raise ValueError("user_id cannot be empty")

    try:
        results = list_escalation_policies(user_ids=[user_id])
        return [result["id"] for result in results["escalation_policies"]]
    except Exception as e:
        utils.handle_api_error(e)
