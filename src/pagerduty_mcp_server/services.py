"""PagerDuty service operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client

logger = logging.getLogger(__name__)

SERVICES_URL = '/services'

VALID_SERVICE_INCLUDES = ['escalation_policy', 'teams']
VALID_SORT_BY = ['name', 'status', 'created_at']

def list_services(*, 
                 team_ids: List[str] = None,
                 include: List[str] = None,
                 query: Optional[str] = None,
                 time_zone: Optional[str] = None,
                 sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """List existing PagerDuty services.
    
    Args:
        team_ids: Filter results to only services assigned to teams with the given IDs
        include: Array of additional details to include. Options: escalation_policy,teams
        query: Filter services whose names contain the search query
        time_zone: Time zone in which dates should be rendered
        sort_by: Sort result by the given field. Options: name,status,created_at
    
    Returns:
        List[Dict[str, Any]]: List of service objects matching the specified criteria
        
    Raises:
        ValueError: If include or sort_by contain invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_SERVICE_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_SERVICE_INCLUDES}"
            )
            
    if sort_by and sort_by not in VALID_SORT_BY:
        raise ValueError(
            f"Invalid sort_by value: {sort_by}. "
            f"Valid values are: {VALID_SORT_BY}"
        )
    
    params = {}
    if team_ids:
        params['team_ids[]'] = team_ids
    if include:
        params['include[]'] = include
    if query:
        params['query'] = query
    if time_zone:
        params['time_zone'] = time_zone
    if sort_by:
        params['sort_by'] = sort_by
        
    try:
        response = client.list_all(SERVICES_URL, params=params)
        return [service['service'] for service in response]
    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        raise RuntimeError(f"Failed to fetch services: {e}") from e

def get_service(service_id: str, *,
                include: List[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given service.
    
    Args:
        service_id: The ID of the service to get
        include: Array of additional details to include. Options: escalation_policy,teams
    
    Returns:
        Dict[str, Any]: Service object with detailed information
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_SERVICE_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_SERVICE_INCLUDES}"
            )
    
    params = {}
    if include:
        params['include[]'] = include
        
    try:
        return client.jget(f"{SERVICES_URL}/{service_id}", params=params)['service']
    except Exception as e:
        logger.error(f"Failed to fetch service {service_id}: {e}")
        raise RuntimeError(f"Failed to fetch service {service_id}: {e}") from e
