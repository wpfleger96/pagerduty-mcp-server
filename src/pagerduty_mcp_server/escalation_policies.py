"""PagerDuty escalation policy operations."""

from typing import List, Dict, Any, Optional
import logging

from . import client
from .parsers import parse_escalation_policy
from . import utils

logger = logging.getLogger(__name__)

ESCALATION_POLICIES_URL = '/escalation_policies'

"""
Escalation Policies API Helpers
"""

def list_escalation_policies(*,
                            query: Optional[str] = None,
                            user_ids: Optional[List[str]] = None,
                            team_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """List escalation policies based on the given criteria.
    
    Args:
        query (str): Filter escalation policies whose names contain the search query (optional)
        user_ids (List[str]): Filter results to only escalation policies that include the given user IDs (optional)
        team_ids (List[str]): Filter results to only escalation policies assigned to teams with the given IDs (optional)
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - escalation_policies (List[Dict[str, Any]]): List of escalation policy objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValueError: If user_ids or team_ids are empty lists
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()
    
    params = {}
    if query:
        params['query'] = query
    if user_ids:
        params['user_ids[]'] = user_ids
    if team_ids:
        params['team_ids[]'] = team_ids
        
    try:
        response = pd_client.list_all(ESCALATION_POLICIES_URL, params=params)
        parsed_response = [parse_escalation_policy(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='escalation_policies') 
    except Exception as e:
        logger.error(f"Failed to fetch escalation policies: {e}")
        raise RuntimeError(f"Failed to fetch escalation policies: {e}") from e

def show_escalation_policy(*,
                        policy_id: str) -> Dict[str, Any]:
    """Get detailed information about a given escalation policy.
    
    Args:
        policy_id (str): The ID of the escalation policy to get
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - escalation_policy (Dict[str, Any]): Escalation policy object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValueError: If policy_id is None or empty
        RuntimeError: If the API request fails or response processing fails
    """

    pd_client = client.get_api_client()

    try:
        response = pd_client.jget(f"{ESCALATION_POLICIES_URL}/{policy_id}")['escalation_policy']
        return utils.api_response_handler(results=parse_escalation_policy(result=response), resource_name='escalation_policy')
    except Exception as e:
        logger.error(f"Failed to fetch escalation policy {policy_id}: {e}")
        raise RuntimeError(f"Failed to fetch escalation policy {policy_id}: {e}") from e


"""
Escalation Policy Helpers
"""

def fetch_escalation_policy_ids(*,
                                user_id: str) -> List[str]:
    """Get the escalation policy IDs for a user.
    
    Args:
        user_id (str): The ID of the user
    
    Returns:
        List[str]: A list of escalation policy IDs associated with the user
    
    Note:
        This is an internal helper function used by other modules.
        Returns an empty list if no policies are found for the user.
    
    Raises:
        RuntimeError: If the API request fails or response processing fails
    """
    
    try:
        results = list_escalation_policies(user_ids=[user_id])
        return [result['id'] for result in results['escalation_policies']]
    except Exception as e:
        logger.error(f"Failed to fetch escalation policies for user {user_id}: {e}")
        raise RuntimeError(f"Failed to fetch escalation policies for user {user_id}: {e}") from e