"""Parser for PagerDuty users."""

from typing import Dict, Any

def parse_user(*,
              result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw user API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw user API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The user ID
            - html_url (str): URL to view the user in PagerDuty
            - name (str): The user's name
            - email (str): The user's email
            - time_zone (str): The user's time zone
            - color (str): The user's color preference
            - avatar_url (str): URL to the user's avatar
            - billed (bool): Whether the user is billed
            - role (str): The user's role
            - description (str): The user's description
            - invitation_sent (bool): Whether an invitation was sent
            - job_title (str): The user's job title
            - locale (str): The user's locale
            - type (str): The user's type
            - summary (str): The user's summary
            - teams (List[Dict]): List of teams with id, type, summary, and html_url
            - contact_methods (List[Dict]): List of contact methods with id, type, summary, and html_url
            - notification_rules (List[Dict]): List of notification rules with id, type, summary, and html_url

    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "html_url": result.get("html_url"),
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
                "summary": team.get("summary"),
                "html_url": team.get("html_url")
            }
            for team in result.get("teams", [])
        ],
        "contact_methods": [
            {
                "id": method.get("id"),
                "type": method.get("type"),
                "summary": method.get("summary"),
                "html_url": method.get("html_url")
            }
            for method in result.get("contact_methods", [])
        ],
        "notification_rules": [
            {
                "id": rule.get("id"),
                "type": rule.get("type"),
                "summary": rule.get("summary"),
                "html_url": rule.get("html_url")
            }
            for rule in result.get("notification_rules", [])
        ]
    } 