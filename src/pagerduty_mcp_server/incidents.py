"""PagerDuty incident operations."""

from typing import List, Dict, Any, Optional, Union
import logging

from .client import get_api_client
from .users import get_user_context
from . import incident_processor

logger = logging.getLogger(__name__)

INCIDENTS_URL = '/incidents'

VALID_STATUSES = ['triggered', 'acknowledged', 'resolved']
DEFAULT_STATUSES = ['triggered', 'acknowledged']

def list_incidents(*, 
                  service_ids: List[str] = None, 
                  team_ids: List[str] = None, 
                  statuses: List[str] = None, 
                  use_my_teams: bool = True,
                  date_range: Optional[str] = None,
                  since: Optional[str] = None,
                  until: Optional[str] = None) -> List[Dict[str, Any]]:
    """List PagerDuty incidents based on specified filters.
    
    Provides a flexible interface for querying PagerDuty incidents with support
    for filtering by teams, services, status, and date ranges. When use_my_teams
    is True (default), automatically uses the current user's team context.
    
    Args:
        service_ids: Optional list of service IDs to filter by
        team_ids: Optional list of team IDs to filter by
        statuses: Optional list of status values to filter by
        use_my_teams: Whether to use the current user's teams/services context (default: True)
        date_range: When set to "all", the since and until parameters are ignored
        since: Start of date range (ISO8601 format). Default is 1 month ago
        until: End of date range (ISO8601 format). Default is now
    
    Returns:
        List[Dict[str, Any]]: List of incident objects matching the specified criteria
    
    Raises:
        ValueError: If the parameter combination is invalid or if status values are invalid
    """

    client = get_api_client()
    
    if statuses is None:
        statuses = DEFAULT_STATUSES
    else:
        invalid_statuses = [s for s in statuses if s not in VALID_STATUSES]
        if invalid_statuses:
            raise ValueError(f"Invalid status values: {invalid_statuses}. Valid values are: {VALID_STATUSES}")
    
    if use_my_teams:
        if service_ids is not None or team_ids is not None:
            raise ValueError(
                "Cannot specify service_ids or team_ids when use_my_teams is True. "
                "Either set use_my_teams=False or remove service_ids/team_ids parameters."
            )
        team_ids, service_ids = get_user_context()
    else:
        if service_ids is None and team_ids is None:
            raise ValueError(
                "Must specify at least service_ids or team_ids when use_my_teams is False."
            )
    
    params = {'statuses': statuses}
    if service_ids:
        params['service_ids'] = service_ids
    if team_ids:
        params['team_ids'] = team_ids
        
    if date_range == 'all':
        pass
    else:
        if since is not None:
            params['since'] = since
        if until is not None:
            params['until'] = until
    
    try:
        incidents = client.list_all(INCIDENTS_URL, params=params)
        return incident_processor.process_incidents(incidents)
    except Exception as e:
        logger.error(f"Failed to fetch or process incidents: {e}")
        raise RuntimeError(f"Failed to fetch or process incidents: {e}") from e

def get_incident(*,
                 id: Union[str, int]) -> Dict[str, Any]:
    """Get detailed information about a given incident.

    Args:
        id: The ID or number of the incident to get

    Returns:
        Dict[str, Any]: Incident object with detailed information
    """

    if id is None:
        raise ValueError("Incident ID is required")

    client = get_api_client()

    params = {}
    
    try:
        incident_str = str(id)
        incident = client.jget(f"{INCIDENTS_URL}/{incident_str}", params=params)["incident"]
        return incident_processor.process_incident(incident)
    except Exception as e:
        logger.error(f"Failed to fetch or process incident {id}: {e}")
        raise RuntimeError(f"Failed to fetch or process incident {id}: {e}") from e
