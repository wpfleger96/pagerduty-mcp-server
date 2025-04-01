"""PagerDuty schedule operations."""

from typing import Dict, Any, Optional
import logging

from . import client
from .parsers import parse_schedule, parse_user
from . import utils

logger = logging.getLogger(__name__)

SCHEDULES_URL = '/schedules'

"""
Schedules API Helpers
"""

def list_schedules(*,
                   query: Optional[str] = None,
                   limit: Optional[int] = None) -> Dict[str, Any]:
    """List existing PagerDuty schedules. Returns all schedules that match the given search criteria.

    Args:
        query (str): Filter schedules whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: A dictionary containing:
            - schedules (List[Dict[str, Any]]): List of schedule objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Total number of results
                - description (str): Description of the results
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()

    params = {}
    if query:
        params['query'] = query
    if limit:
        params['limit'] = limit

    try:
        response = pd_client.list_all(SCHEDULES_URL, params=params)
        parsed_response = [parse_schedule(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='schedules')
    except Exception as e:
        utils.handle_api_error(e)

def show_schedule(*,
                 schedule_id: str,
                 since: Optional[str] = None,
                 until: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given schedule, including its configuration and current state.

    Args:
        schedule_id (str): The ID of the schedule to get
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now

    Returns:
        Dict[str, Any]: A dictionary containing:
            - schedule (Dict[str, Any]): Schedule object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Always 1 for single resource responses
                - description (str): Description of the result
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        ValueError: If schedule_id is None or empty
        ValidationError: If since or until parameters are not valid ISO8601 timestamps
        RuntimeError: If the API request fails or response processing fails
    """

    if not schedule_id:
        raise ValueError("schedule_id cannot be empty")

    pd_client = client.get_api_client()

    params = {}
    if since:
        utils.validate_iso8601_timestamp(since, 'since')
        params['since'] = since
    if until:
        utils.validate_iso8601_timestamp(until, 'until')
        params['until'] = until

    try:
        response = pd_client.jget(f"{SCHEDULES_URL}/{schedule_id}", params=params)
        try:
            schedule_data = response['schedule']
        except KeyError:
            raise RuntimeError(f"Failed to fetch schedule {schedule_id}: Response missing 'schedule' field")
            
        return utils.api_response_handler(results=parse_schedule(result=schedule_data), resource_name='schedule')
    except Exception as e:
        utils.handle_api_error(e)

def list_users_oncall(*,
                      schedule_id: str,
                      since: Optional[str] = None,
                      until: Optional[str] = None) -> Dict[str, Any]:
    """List the users on call for a given schedule during the specified time range. Returns a list of users who are or will be on call during the specified period.

    Args:
        schedule_id (str): The ID of the schedule to list users on call for
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now

    Returns:
        Dict[str, Any]: A dictionary containing:
            - users (List[Dict[str, Any]]): List of user objects on call during the specified time range
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Total number of users on call
                - description (str): Description of the results
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        ValueError: If schedule_id is None or empty
        ValidationError: If since or until parameters are not valid ISO8601 timestamps
        RuntimeError: If the API request fails or response processing fails
    """

    if not schedule_id:
        raise ValueError("schedule_id cannot be empty")

    pd_client = client.get_api_client()

    params = {}
    if since:
        utils.validate_iso8601_timestamp(since, 'since')
        params['since'] = since
    if until:
        utils.validate_iso8601_timestamp(until, 'until')
        params['until'] = until

    try:
        response = pd_client.jget(f"{SCHEDULES_URL}/{schedule_id}/users", params=params)
        try:
            users_data = response['users']
        except KeyError:
            raise RuntimeError(f"Failed to fetch users on call for schedule {schedule_id}: Response missing 'users' field")
            
        return utils.api_response_handler(results=[parse_user(result=user) for user in users_data], resource_name='users')
    except Exception as e:
        utils.handle_api_error(e)
