"""PagerDuty on-call operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .client import create_client
from .parsers import parse_oncall

logger = logging.getLogger(__name__)

ONCALLS_URL = "/oncalls"

"""
On-Calls API Helpers
"""


def list_oncalls(
    *,
    schedule_ids: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    escalation_policy_ids: Optional[List[str]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: Optional[int] = None,
    earliest: Optional[bool] = None,
) -> Dict[str, Any]:
    """List the on-call entries during a given time range.
    An oncall-entry contains the user that is on-call for the given schedule, escalation policy, or time range and also includes the schedule and escalation policy that the user is on-call for. Exposed in `get_oncalls`.

    Args:
        schedule_ids (List[str]): Return only on-calls for the specified schedule IDs (optional)
        user_ids (List[str]): Return only on-calls for the specified user IDs (optional)
        escalation_policy_ids (List[str]): Return only on-calls for the specified escalation policy IDs (optional)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
        limit (int): Limit the number of results returned (optional)
        earliest (bool): If True, only returns the earliest on-call for each combination of escalation policy, escalation level, and user. Useful for determining when the "next" on-calls are for a given set of filters. (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of on-call entries with user, schedule, and escalation policy information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params = {}
    if schedule_ids:
        params["schedule_ids[]"] = schedule_ids
    if user_ids:
        params["user_ids[]"] = user_ids
    if escalation_policy_ids:
        params["escalation_policy_ids[]"] = escalation_policy_ids
    if since:
        utils.validate_iso8601_timestamp(since, "since")
        params["since"] = since
    if until:
        utils.validate_iso8601_timestamp(until, "until")
        params["until"] = until
    if limit:
        params["limit"] = limit
    if earliest is not None:
        params["earliest"] = earliest

    try:
        response = pd_client.list_all(ONCALLS_URL, params=params)
        parsed_response = [parse_oncall(result=result) for result in response]
        return utils.api_response_handler(
            results=parsed_response, resource_name="oncalls"
        )
    except Exception as e:
        utils.handle_api_error(e)
