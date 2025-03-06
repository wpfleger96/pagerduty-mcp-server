"""PagerDuty schedule operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client

logger = logging.getLogger(__name__)

ONCALLS_URL = '/oncalls'
SCHEDULES_URL = '/schedules'

VALID_SCHEDULE_INCLUDES = ['teams', 'users', 'escalation_policies', 'schedule_layers']

def list_schedules(*, 
                  query: Optional[str] = None,
                  include: List[str] = None) -> List[Dict[str, Any]]:
    """List the on-call schedules.
    
    Args:
        query: Filter schedules whose names contain the search query
        include: Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers
    
    Returns:
        List[Dict[str, Any]]: List of schedule objects
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_SCHEDULE_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_SCHEDULE_INCLUDES}"
            )
    
    params = {}
    if query:
        params['query'] = query
    if include:
        params['include[]'] = include
        
    try:
        response = client.list_all(SCHEDULES_URL, params=params)
        return [schedule['schedule'] for schedule in response]
    except Exception as e:
        logger.error(f"Failed to fetch schedules: {e}")
        raise RuntimeError(f"Failed to fetch schedules: {e}") from e

def get_schedule(schedule_id: str, *,
                since: Optional[str] = None,
                until: Optional[str] = None,
                include: List[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given schedule.
    
    Args:
        schedule_id: The ID of the schedule to get
        since: The start of the time range over which you want to search
        until: The end of the time range over which you want to search
        include: Array of additional details to include. Options: teams,users,escalation_policies,schedule_layers
    
    Returns:
        Dict[str, Any]: Schedule object with detailed information
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_SCHEDULE_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_SCHEDULE_INCLUDES}"
            )
    
    params = {}
    if since:
        params['since'] = since
    if until:
        params['until'] = until
    if include:
        params['include[]'] = include
        
    try:
        return client.jget(f"{SCHEDULES_URL}/{schedule_id}", params=params)['schedule']
    except Exception as e:
        logger.error(f"Failed to fetch schedule {schedule_id}: {e}")
        raise RuntimeError(f"Failed to fetch schedule {schedule_id}: {e}") from e
