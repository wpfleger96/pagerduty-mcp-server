"""Parser for PagerDuty teams."""

from typing import Dict, Any

def parse_team(*,
              result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw team API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw team API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The team ID
            - name (str): The team name
            - description (str): The team description
            - type (str): The team type
            - summary (str): The team summary
            - default_role (str): Default role for team members
            - parent (Dict): Parent team information if this is a sub-team
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "description": result.get("description"),
        "type": result.get("type"),
        "summary": result.get("summary"),
        "default_role": result.get("default_role"),
        "parent": result.get("parent")
    }
