"""PagerDuty user operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client

logger = logging.getLogger(__name__)

USERS_URL = '/users'
SERVICES_URL = '/services'

def show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile.
    
    Returns:
        Dict[str, Any]: The user object containing profile information
        
    Raises:
        RuntimeError: If the API call fails
    """

    client = get_api_client()
    try:
        user = client.jget(USERS_URL + '/me')['user']
        return user
    except Exception as e:
        logger.error(f"Failed to fetch current user: {e}")
        raise RuntimeError(f"Failed to fetch current user: {e}") from e

def get_user_context() -> tuple[List[str], List[str]]:
    """Get the current user's teams and associated services.
    
    Fetches the user's team memberships and then queries for all services
    associated with those teams.
    
    Returns:
        tuple[List[str], List[str]]: A tuple of (team_ids, service_ids)
        
    Raises:
        RuntimeError: If the API calls fail
    """

    client = get_api_client()
    try:
        user = show_current_user()
        team_ids = [team['id'] for team in user['teams']]
        
        params = {'team_ids': team_ids}
        services_response = client.list_all(SERVICES_URL, params=params)
        service_ids = [service['id'] for service in services_response]
        
        return team_ids, service_ids
    except Exception as e:
        logger.error(f"Failed to fetch user context: {e}")
        raise RuntimeError(f"Failed to fetch user context: {e}") from e
