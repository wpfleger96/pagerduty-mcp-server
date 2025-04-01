"""PagerDuty on-call operations."""

from typing import List, Dict, Any, Optional
import logging

from . import client
from .parsers import parse_oncall
from . import utils

logger = logging.getLogger(__name__)

ONCALLS_URL = '/oncalls'

"""
On-Calls API Helpers
"""

def list_oncalls(*,
                schedule_ids: Optional[List[str]] = None,
                user_ids: Optional[List[str]] = None,
                escalation_policy_ids: Optional[List[str]] = None,
                since: Optional[str] = None,
                until: Optional[str] = None,
                limit: Optional[int] = None,
                earliest: Optional[bool] = None) -> Dict[str, Any]:
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
        schedule_ids (List[str]): Return only on-calls for the specified schedule IDs (optional)
        user_ids (List[str]): Return only on-calls for the specified user IDs (optional)
        escalation_policy_ids (List[str]): Return only on-calls for the specified escalation policy IDs (optional)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
        limit (int): Limit the number of results returned (optional)
        earliest (bool): If True, only returns the earliest on-call for each combination of escalation policy, escalation level, and user. Useful for determining when the "next" on-calls are for a given set of filters. (optional)

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
                - escalation_level (int): Escalation level for this on-call
                - start (str): Start time of the on-call period in ISO8601 format
                - end (str): End time of the on-call period in ISO8601 format
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

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
                },
                ...
            ]
        }

    Raises:
        ValueError: If any of the ID lists are empty
        ValidationError: If since or until parameters are not valid ISO8601 timestamps
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()

    params = {}
    if schedule_ids:
        params['schedule_ids[]'] = schedule_ids
    if user_ids:
        params['user_ids[]'] = user_ids
    if escalation_policy_ids:
        params['escalation_policy_ids[]'] = escalation_policy_ids
    if since:
        utils.validate_iso8601_timestamp(since, 'since')
        params['since'] = since
    if until:
        utils.validate_iso8601_timestamp(until, 'until')
        params['until'] = until
    if limit:
        params['limit'] = limit
    if earliest is not None:
        params['earliest'] = earliest

    try:
        response = pd_client.list_all(ONCALLS_URL, params=params)
        parsed_response = [parse_oncall(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='oncalls')
    except Exception as e:
        utils.handle_api_error(e)
