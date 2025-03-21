"""Parser for PagerDuty schedules."""

from typing import Dict, Any

def parse_schedule(*,
                   result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw schedule API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw schedule API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The schedule ID
            - html_url (str): URL to view the schedule in PagerDuty
            - name (str): The schedule name
            - summary (str): The schedule summary
            - description (str): The schedule description
            - time_zone (str): The schedule's time zone
            - escalation_policies (List[Dict]): List of escalation policies with id, summary, and html_url
            - teams (List[Dict]): List of teams with id, summary, and html_url
            - schedule_layers (List[Dict]): List of schedule layers, each containing:
                - id (str): Layer ID
                - name (str): Layer name
                - start (str): Start time
                - end (str): End time
                - users (List[Dict]): List of users with id, summary, and html_url

    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "html_url": result.get("html_url"),
        "name": result.get("name"),
        "summary": result.get("summary"),
        "description": result.get("description"),
        "time_zone": result.get("time_zone"),
        "escalation_policies": [
            {
                "id": policy.get("id"),
                "summary": policy.get("summary"),
                "html_url": policy.get("html_url")
            }
            for policy in result.get("escalation_policies", [])
        ],
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary"),
                "html_url": team.get("html_url")
            }
            for team in result.get("teams", [])
        ],
        "schedule_layers": [
            {
                "id": layer.get("id"),
                "name": layer.get("name"),
                "start": layer.get("start"),
                "end": layer.get("end"),
                "users": [
                    {
                        "id": user.get("user", {}).get("id"),
                        "summary": user.get("user", {}).get("summary"),
                        "html_url": user.get("user", {}).get("html_url")
                    }
                    for user in layer.get("users", [])
                ]
            }
            for layer in result.get("schedule_layers", [])
        ]
    } 