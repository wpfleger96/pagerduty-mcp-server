"""PagerDuty team operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client

logger = logging.getLogger(__name__)

TEAMS_URL = '/teams'

VALID_TEAM_INCLUDES = ['members', 'notification_rules']

def list_teams(*, 
               query: Optional[str] = None,
               include: List[str] = None) -> List[Dict[str, Any]]:
    """List teams in your PagerDuty account.
    
    Args:
        query: Filter teams whose names contain the search query
        include: Array of additional details to include. Options: members,notification_rules
    
    Returns:
        List[Dict[str, Any]]: List of team objects matching the specified criteria
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_TEAM_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_TEAM_INCLUDES}"
            )
    
    params = {}
    if query:
        params['query'] = query
    if include:
        params['include[]'] = include
        
    try:
        response = client.list_all(TEAMS_URL, params=params)
        return [team['team'] for team in response]
    except Exception as e:
        logger.error(f"Failed to fetch teams: {e}")
        raise RuntimeError(f"Failed to fetch teams: {e}") from e

def get_team(*,
             team_id: str,
             include: List[str] = None) -> Dict[str, Any]:
    """Get detailed information about a given team.
    
    Args:
        team_id: The ID of the team to get
        include: Array of additional details to include. Options: members,notification_rules
    
    Returns:
        Dict[str, Any]: Team object with detailed information
        
    Raises:
        ValueError: If include contains invalid values
    """

    if team_id is None:
        raise ValueError("team_id must be specified")

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_TEAM_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_TEAM_INCLUDES}"
            )
    
    params = {}
    if include:
        params['include[]'] = include
        
    try:
        return client.jget(f"{TEAMS_URL}/{team_id}", params=params)['team']
    except Exception as e:
        logger.error(f"Failed to fetch team {team_id}: {e}")
        raise RuntimeError(f"Failed to fetch team {team_id}: {e}") from e
