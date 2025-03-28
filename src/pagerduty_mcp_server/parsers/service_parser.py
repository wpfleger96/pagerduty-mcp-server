"""Parser for PagerDuty services."""

from typing import Dict, Any

def parse_service(*,
                 result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw service API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw service API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The service ID
            - html_url (str): URL to view the service in PagerDuty
            - name (str): The service name
            - description (str): The service description
            - status (str): Current status of the service
            - created_at (str): Creation timestamp
            - updated_at (str): Last update timestamp
            - teams (List[Dict]): List of teams with id, summary, and html_url
            - integrations (List[Dict]): List of integrations with id, summary, and html_url
    
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
        "status": result.get("status"),
        "created_at": result.get("created_at"),
        "updated_at": result.get("updated_at"),
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary"),
                "html_url": team.get("html_url")
            }
            for team in result.get("teams", [])
        ],
        "integrations": [
            {
                "id": integration.get("id"),
                "summary": integration.get("summary"),
                "html_url": integration.get("html_url")
            }
            for integration in result.get("integrations", [])
        ]
    } 