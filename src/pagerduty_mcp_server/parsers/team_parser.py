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
            - html_url (str): URL to view the team in PagerDuty
            - name (str): The team name
            - description (str): The team description
            - type (str): The team type
            - summary (str): The team summary
            - default_role (str): Default role for team members
            - parent (Dict): Parent team information if this is a sub-team, containing:
                - id (str): Parent team ID
                - type (str): Parent team type
                - summary (str): Parent team summary
                - html_url (str): URL to view the parent team in PagerDuty
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "html_url": result.get("html_url"),
        "name": result.get("name"),
        "description": result.get("description"),
        "type": result.get("type"),
        "summary": result.get("summary"),
        "default_role": result.get("default_role"),
        "parent": {
            "id": result.get("parent", {}).get("id"),
            "type": result.get("parent", {}).get("type"),
            "summary": result.get("parent", {}).get("summary"),
            "html_url": result.get("parent", {}).get("html_url")
        } if result.get("parent") else None
    }
