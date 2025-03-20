"""PagerDuty incident operations."""

from typing import List, Dict, Any, Optional, Union
import logging

from . import client
from . import utils
from .parsers import parse_incident

logger = logging.getLogger(__name__)

INCIDENTS_URL = '/incidents'

VALID_STATUSES = ['triggered', 'acknowledged', 'resolved']
DEFAULT_STATUSES = ['triggered', 'acknowledged']
VALID_URGENCIES = ['high', 'low']
DEFAULT_URGENCIES = ['high', 'low']

"""
Incidents API Helpers
"""

def list_incidents(*, 
                  service_ids: Optional[List[str]] = None, 
                  team_ids: Optional[List[str]] = None, 
                  statuses: Optional[List[str]] = None,
                  urgencies: Optional[List[str]] = None,
                  since: Optional[str] = None,
                  until: Optional[str] = None) -> Dict[str, Any]:
    """List PagerDuty incidents based on specified filters.
    
    Args:
        service_ids (List[str]): List of PagerDuty service IDs to filter by (optional)
        team_ids (List[str]): List of PagerDuty team IDs to filter by (optional)
        statuses (List[str]): List of status values to filter by (optional). Valid values are:
            - 'triggered' - The incident is currently active (included by default)
            - 'acknowledged' - The incident has been acknowledged by a user (included by default)
            - 'resolved' - The incident has been resolved (excluded by default)
        urgencies (List[str]): List of urgency values to filter by (optional). Valid values are:
            - 'high' - High urgency incidents (included by default)
            - 'low' - Low urgency incidents (included by default)
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - incidents (List[Dict[str, Any]]): List of incident objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
    
    Raises:
        ValueError: If invalid status or urgency values are provided
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    if statuses is None:
        statuses = DEFAULT_STATUSES
    else:
        invalid_statuses = [s for s in statuses if s not in VALID_STATUSES]
        if invalid_statuses:
            raise ValueError(f"Invalid status values: {invalid_statuses}. Valid values are: {VALID_STATUSES}")
        
    if urgencies is None:
        urgencies = DEFAULT_URGENCIES
    else:
        invalid_urgencies = [u for u in urgencies if u not in VALID_URGENCIES]
        if invalid_urgencies:
            raise ValueError(f"Invalid urgency values: {invalid_urgencies}. Valid values are: {VALID_URGENCIES}")
    
    params = {'statuses': statuses, 'urgencies': urgencies}
    if service_ids:
        params['service_ids'] = service_ids
    if team_ids:
        params['team_ids'] = team_ids
    if since is not None:
        params['since'] = since
    if until is not None:
        params['until'] = until
    
    try:
        response = pd_client.list_all(INCIDENTS_URL, params=params)
        parsed_response = [parse_incident(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='incidents')
    except Exception as e:
        logger.error(f"Failed to fetch or process incidents: {e}")
        raise RuntimeError(f"Failed to fetch or process incidents: {e}") from e

def show_incident(*,
                 incident_id: str) -> Dict[str, Any]:
    """Get detailed information about a given incident.

    Args:
        incident_id (str): The ID or number of the incident to get

    Returns:
        Dict[str, Any]: A dictionary containing:
            - incident (Dict[str, Any]): Incident object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
    
    Raises:
        ValueError: If incident_id is None or empty
        RuntimeError: If the API request fails or response processing fails
    """

    if not incident_id:
        raise ValueError("incident_id cannot be empty")

    pd_client = client.get_api_client()
    
    try:
        response = pd_client.jget(f"{INCIDENTS_URL}/{incident_id}")['incident']
        return utils.api_response_handler(results=parse_incident(result=response), resource_name='incident')
    except Exception as e:
        logger.error(f"Failed to fetch or process incident {incident_id}: {e}")
        raise RuntimeError(f"Failed to fetch or process incident {incident_id}: {e}") from e
