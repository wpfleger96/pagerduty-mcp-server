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
                until: Optional[str] = None) -> Dict[str, Any]:
    """List the on-call entries during a given time range.
    
    Args:
        schedule_ids (List[str]): Return only on-calls for the specified schedule IDs (optional)
        user_ids (List[str]): Return only on-calls for the specified user IDs (optional)
        escalation_policy_ids (List[str]): Return only on-calls for the specified escalation policy IDs (optional)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - oncalls (List[Dict[str, Any]]): List of on-call entries matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
    
    Raises:
        ValueError: If any of the ID lists are empty
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
        params['since'] = since
    if until:
        params['until'] = until
        
    try:
        response = pd_client.list_all(ONCALLS_URL, params=params)
        parsed_response = [parse_oncall(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='oncalls')
    except Exception as e:
        logger.error(f"Failed to fetch on-call entries: {e}")
        raise RuntimeError(f"Failed to fetch on-call entries: {e}") from e
