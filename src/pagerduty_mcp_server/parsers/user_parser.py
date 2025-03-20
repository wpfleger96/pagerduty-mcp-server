"""Parser for PagerDuty users."""

from typing import Dict, Any

def parse_user(*,
              result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw user API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw user API response

    Returns:
        Dict[str, Any]: The parsed user
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "email": result.get("email"),
        "time_zone": result.get("time_zone"),
        "color": result.get("color"),
        "avatar_url": result.get("avatar_url"),
        "billed": result.get("billed"),
        "role": result.get("role"),
        "description": result.get("description"),
        "invitation_sent": result.get("invitation_sent"),
        "job_title": result.get("job_title"),
        "locale": result.get("locale"),
        "type": result.get("type"),
        "summary": result.get("summary"),
        "teams": [
            {
                "id": team.get("id"),
                "type": team.get("type"),
                "summary": team.get("summary")
            }
            for team in result.get("teams", [])
        ],
        "contact_methods": [
            {
                "id": method.get("id"),
                "type": method.get("type"),
                "summary": method.get("summary")
            }
            for method in result.get("contact_methods", [])
        ],
        "notification_rules": [
            {
                "id": rule.get("id"),
                "type": rule.get("type"),
                "summary": rule.get("summary")
            }
            for rule in result.get("notification_rules", [])
        ]
    } 