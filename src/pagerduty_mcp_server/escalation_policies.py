"""PagerDuty escalation policy operations."""

from typing import List, Dict, Any, Optional
import logging

from .client import get_api_client
from .users import get_user_context

logger = logging.getLogger(__name__)

ESCALATION_POLICIES_URL = '/escalation_policies'

VALID_POLICY_INCLUDES = ['teams', 'services', 'num_loops', 'current_state']
VALID_SORT_BY = ['name', 'description']

def list_escalation_policies(*, 
                           query: Optional[str] = None,
                           user_ids: Optional[List[str]] = None,
                           team_ids: Optional[List[str]] = None,
                           use_my_teams: bool = True,
                           include: Optional[List[str]] = None,
                           sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    """List existing escalation policies.
    
    Args:
        query: Filter escalation policies whose names contain the search query
        user_ids: Filter results to only escalation policies that include the given user IDs
        team_ids: Filter results to only escalation policies assigned to teams with the given IDs
        include: Array of additional details to include. Options: teams,services,num_loops,current_state
        use_my_teams: Whether to use the current user's teams/services context (default: True)
        sort_by: Sort result by the given field. Options: name,description
    
    Returns:
        List[Dict[str, Any]]: List of escalation policy objects matching the specified criteria
        
    Raises:
        ValueError: If include or sort_by contain invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_POLICY_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_POLICY_INCLUDES}"
            )
            
    if sort_by and sort_by not in VALID_SORT_BY:
        raise ValueError(
            f"Invalid sort_by value: {sort_by}. "
            f"Valid values are: {VALID_SORT_BY}"
        )
    
    if use_my_teams:
        if team_ids is not None:
            raise ValueError(
                "Cannot specify team_ids when use_my_teams is True. "
                "Either set use_my_teams=False or remove service_ids parameters."
            )
        team_ids, _service_ids = get_user_context()
    else:
        if team_ids is None:
            raise ValueError(
                "Must specify service_ids when use_my_teams is False."
            )
    
    params = {}
    if query:
        params['query'] = query
    if user_ids:
        params['user_ids[]'] = user_ids
    if team_ids:
        params['team_ids[]'] = team_ids
    if include:
        params['include[]'] = include
    if sort_by:
        params['sort_by'] = sort_by
        
    try:
        response = client.list_all(ESCALATION_POLICIES_URL, params=params)
        return response
    except Exception as e:
        logger.error(f"Failed to fetch escalation policies: {e}")
        raise RuntimeError(f"Failed to fetch escalation policies: {e}") from e

def get_escalation_policy(policy_id: str, *,
                         include: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get detailed information about a given escalation policy.
    
    Args:
        policy_id: The ID of the escalation policy to get
        include: Array of additional details to include. Options: teams,services,num_loops,current_state
    
    Returns:
        Dict[str, Any]: Escalation policy object with detailed information
        
    Raises:
        ValueError: If include contains invalid values
    """

    client = get_api_client()
    
    if include:
        invalid_includes = [i for i in include if i not in VALID_POLICY_INCLUDES]
        if invalid_includes:
            raise ValueError(
                f"Invalid include values: {invalid_includes}. "
                f"Valid values are: {VALID_POLICY_INCLUDES}"
            )
    
    params = {}
    if include:
        params['include[]'] = include
        
    try:
        return client.jget(f"{ESCALATION_POLICIES_URL}/{policy_id}", params=params)['escalation_policy']
    except Exception as e:
        logger.error(f"Failed to fetch escalation policy {policy_id}: {e}")
        raise RuntimeError(f"Failed to fetch escalation policy {policy_id}: {e}") from e
