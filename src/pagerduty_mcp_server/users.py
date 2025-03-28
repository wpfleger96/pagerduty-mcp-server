"""PagerDuty user operations."""

from typing import List, Dict, Any, Optional
import logging

from . import client
from .parsers import parse_user
from . import utils

logger = logging.getLogger(__name__)

USERS_URL = '/users'

"""
Users API Helpers
"""

def show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile including their teams, contact methods, and notification rules.
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - name (str): User's full name
            - email (str): User's email address
            - role (str): User's role in PagerDuty
            - description (str): User's description
            - job_title (str): User's job title
            - teams (List[Dict]): List of teams with id and summary
            - contact_methods (List[Dict]): List of contact methods with id and summary
            - notification_rules (List[Dict]): List of notification rules with id and summary
            - id (str): User's PagerDuty ID
    
    Raises:
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    try:
        response = pd_client.jget(USERS_URL + '/me')['user']
        return parse_user(result=response)
    except Exception as e:
        logger.error(f"Failed to fetch current user: {e}")
        raise RuntimeError(f"Failed to fetch current user: {e}") from e

def list_users(*,
               team_ids: Optional[List[str]] = None,
               query: Optional[str] = None) -> Dict[str, Any]:
    """List users in PagerDuty.
    
    Args:
        team_ids (List[str]): Filter results to only users assigned to teams with the given IDs (optional)
        query (str): Filter users whose names contain the search query (optional)

    Returns:
        Dict[str, Any]: A dictionary containing:
            - users (List[Dict[str, Any]]): List of user objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValueError: If team_ids is an empty list
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    params = {}

    if team_ids:
        params['team_ids[]'] = team_ids
    if query:
        params['query'] = query

    try:
        response = pd_client.list_all(USERS_URL, params=params)
        parsed_response = [parse_user(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='users')
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        raise RuntimeError(f"Failed to fetch users: {e}") from e

def show_user(*,
              user_id: str) -> Dict[str, Any]:
    """Get detailed information about a given user.
    
    Args:
        user_id (str): The ID of the user to fetch
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - user (Dict[str, Any]): User object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValueError: If user_id is None or empty
        RuntimeError: If the API request fails or response processing fails
    """

    if not user_id:
        raise ValueError("User ID is required")

    pd_client = client.get_api_client()
    try:
        response = pd_client.jget(f"{USERS_URL}/{user_id}")['user']
        return utils.api_response_handler(results=parse_user(result=response), resource_name='user')
    except Exception as e:
        logger.error(f"Failed to fetch user {user_id}: {e}")
        raise RuntimeError(f"Failed to fetch user {user_id}: {e}") from e
