"""PagerDuty on-call operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client

logger = logging.getLogger(__name__)

ONCALLS_URL = '/oncalls'

VALID_ONCALL_INCLUDES = ['users', 'schedules', 'escalation_policies']


def list_oncall(*, 
                schedule_ids: List[str] = None,
                user_ids: List[str] = None,
                escalation_policy_ids: List[str] = None,
                since: Optional[str] = None,
                until: Optional[str] = None,
                include: List[str] = None) -> List[Dict[str, Any]]:
    """List the on-call entries during a given time range.
    
    Args:
        schedule_ids: Return only on-calls for the specified schedule IDs
        user_ids: Return only on-calls for the specified user IDs
        escalation_policy_ids: Return only on-calls for the specified escalation policy IDs
        since: The start of the time range over which you want to search
        until: The end of the time range over which you want to search
        include: Array of additional details to include. Options: users,schedules,escalation_policies
    
    Returns:
        List[Dict[str, Any]]: List of on-call entries matching the specified criteria
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_ONCALL_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_ONCALL_INCLUDES}"
            )
    
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
    if include:
        params['include[]'] = include
        
    try:
        response = client.list_all(ONCALLS_URL, params=params)
        return response
    except Exception as e:
        logger.error(f"Failed to fetch on-call entries: {e}")
        raise RuntimeError(f"Failed to fetch on-call entries: {e}") from e
