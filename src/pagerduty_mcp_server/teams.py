"""PagerDuty team operations."""

from typing import List, Dict, Any, Optional
import logging

from . import client
from .parsers import parse_team
from . import utils

logger = logging.getLogger(__name__)

TEAMS_URL = '/teams'

"""
Teams API Helpers
"""

def list_teams(*, 
               query: Optional[str] = None) -> Dict[str, Any]:
    """List teams in your PagerDuty account.
    
    Args:
        query (str): Filter teams whose names contain the search query (optional)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - teams (List[Dict[str, Any]]): List of team objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    params = {}
    if query:
        params['query'] = query
        
    try:
        response = pd_client.list_all(TEAMS_URL, params=params)
        parsed_response = [parse_team(result=team) for team in response]
        return utils.api_response_handler(results=parsed_response, resource_name='teams')
    except Exception as e:
        logger.error(f"Failed to fetch teams: {e}")
        raise RuntimeError(f"Failed to fetch teams: {e}") from e

def show_team(*,
             team_id: str) -> Dict[str, Any]:
    """Get detailed information about a given team.
    
    Args:
        team_id (str): The ID of the team to get
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - team (Dict[str, Any]): Team object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValueError: If team_id is None or empty
        RuntimeError: If the API request fails or response processing fails
    """

    if team_id is None:
        raise ValueError("team_id must be specified")

    pd_client = client.get_api_client()
        
    try:
        response = pd_client.jget(f"{TEAMS_URL}/{team_id}")['team']
        return utils.api_response_handler(results=parse_team(result=response), resource_name='team')
    except Exception as e:
        logger.error(f"Failed to fetch team {team_id}: {e}")
        raise RuntimeError(f"Failed to fetch team {team_id}: {e}") from e


"""
Teams Helpers
"""

def fetch_team_ids(*,
                   user: Dict[str, Any]) -> List[str]:
    """Get the team IDs for a user.
    
    Args:
        user (Dict[str, Any]): The user object containing a teams field with team information
    
    Returns:
        List[str]: A list of team IDs from the user's teams
    
    Note:
        This is an internal helper function used by other modules.
        Returns an empty list if user is None or has no teams.
    """
    
    return [team['id'] for team in user['teams']]
