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
            - name (str): The service name
            - description (str): The service description
            - status (str): Current status of the service
            - created_at (str): Creation timestamp
            - updated_at (str): Last update timestamp
            - teams (List[Dict]): List of teams with id and summary
            - integrations (List[Dict]): List of integrations with id and summary
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "description": result.get("description"),
        "status": result.get("status"),
        "created_at": result.get("created_at"),
        "updated_at": result.get("updated_at"),
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary")
            }
            for team in result.get("teams", [])
        ],
        "integrations": [
            {
                "id": integration.get("id"),
                "summary": integration.get("summary")
            }
            for integration in result.get("integrations", [])
        ]
    } 