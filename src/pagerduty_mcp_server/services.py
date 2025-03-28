"""PagerDuty service operations."""

from typing import List, Dict, Any, Optional
import logging

from . import client
from .parsers import parse_service
from . import utils

logger = logging.getLogger(__name__)

SERVICES_URL = '/services'

"""
Services API Helpers
"""

def list_services(*, 
                 team_ids: Optional[List[str]] = None,
                 query: Optional[str] = None) -> Dict[str, Any]:
    """List existing PagerDuty services.
    
    Args:
        team_ids (List[str]): Filter results to only services assigned to teams with the given IDs (optional)
        query (str): Filter services whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - services (List[Dict[str, Any]]): List of service objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
    
    Raises:
        ValueError: If team_ids is an empty list
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    if team_ids is not None and not team_ids:
        raise ValueError("team_ids cannot be an empty list")
    
    params = {}
    if team_ids:
        params['team_ids[]'] = team_ids  # PagerDuty API expects array parameters with [] suffix
    if query:
        params['query'] = query
        
    try:
        response = pd_client.list_all(SERVICES_URL, params=params)
        parsed_response = [parse_service(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='services')
    except Exception as e:
        logger.error(f"Failed to fetch services: {e}")
        raise RuntimeError(f"Failed to fetch services: {e}") from e

def show_service(*,
                service_id: str) -> Dict[str, Any]:
    """Get detailed information about a given service.
    
    Args:
        service_id (str): The ID of the service to get
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - service (Dict[str, Any]): Service object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
    
    Raises:
        ValueError: If service_id is None or empty
        RuntimeError: If the API request fails or response processing fails
    """

    if not service_id:
        raise ValueError("service_id cannot be empty")

    pd_client = client.get_api_client()
        
    try:
        response = pd_client.jget(f"{SERVICES_URL}/{service_id}")['service']
        return utils.api_response_handler(results=parse_service(result=response), resource_name='service')
    except Exception as e:
        logger.error(f"Failed to fetch service {service_id}: {e}")
        raise RuntimeError(f"Failed to fetch service {service_id}: {e}") from e


"""
Services Helpers
"""

def fetch_service_ids(*,
                      team_ids: List[str]) -> List[str]:
    """Get the service IDs for a list of team IDs.
    
    Args:
        team_ids (List[str]): A list of team IDs
    
    Returns:
        List[str]: A list of service IDs
    """
    if not team_ids:
        raise ValueError("Team IDs must be specified")
    
    pd_client = client.get_api_client()
    params = {'team_ids[]': team_ids}  # PagerDuty API expects array parameters with [] suffix
    try:
        services_response = pd_client.list_all(SERVICES_URL, params=params)
        parsed_response = [parse_service(result=result) for result in services_response]
        return [service['id'] for service in parsed_response]
    except Exception as e:
        logger.error(f"Failed to fetch services for teams {team_ids}: {e}")
        raise RuntimeError(f"Failed to fetch services for teams {team_ids}: {e}") from e
