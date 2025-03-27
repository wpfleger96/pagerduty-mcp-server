"""PagerDuty schedule operations."""

from typing import Dict, Any, Optional
import logging

from . import client
from .parsers import parse_schedule
from . import utils

logger = logging.getLogger(__name__)

SCHEDULES_URL = '/schedules'

"""
Schedules API Helpers
"""

def list_schedules(*, query: Optional[str] = None) -> Dict[str, Any]:
    """List existing PagerDuty schedules.
    
    Args:
        query (str): Filter schedules whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - schedules (List[Dict[str, Any]]): List of schedule objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
    
    Raises:
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    params = {}
    if query:
        params['query'] = query
        
    try:
        response = pd_client.list_all(SCHEDULES_URL, params=params)
        parsed_response = [parse_schedule(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='schedules')
    except Exception as e:
        logger.error(f"Failed to fetch schedules: {e}")
        raise RuntimeError(f"Failed to fetch schedules: {e}") from e

def show_schedule(*,
                 schedule_id: str,
                 since: Optional[str] = None,
                 until: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given schedule.
    
    Args:
        schedule_id (str): The ID of the schedule to get
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - schedule (Dict[str, Any]): Schedule object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
    
    Raises:
        ValueError: If schedule_id is None
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    params = {}
    if since:
        params['since'] = since
    if until:
        params['until'] = until
        
    try:
        response = pd_client.jget(f"{SCHEDULES_URL}/{schedule_id}", params=params)['schedule']
        return utils.api_response_handler(results=parse_schedule(result=response), resource_name='schedule')
    except Exception as e:
        logger.error(f"Failed to fetch schedule {schedule_id}: {e}")
        raise RuntimeError(f"Failed to fetch schedule {schedule_id}: {e}") from e
