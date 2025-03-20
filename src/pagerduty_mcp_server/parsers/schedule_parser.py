"""Parser for PagerDuty schedules."""

from typing import Dict, Any

def parse_schedule(*,
                   result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw schedule API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw schedule API response

    Returns:
        Dict[str, Any]: The parsed schedule
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "name": result.get("name"),
        "summary": result.get("summary"),
        "description": result.get("description"),
        "time_zone": result.get("time_zone"),
        "escalation_policies": [
            {
                "id": policy.get("id"),
                "summary": policy.get("summary")
            }
            for policy in result.get("escalation_policies", [])
        ],
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary")
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
                        "summary": user.get("user", {}).get("summary")
                    }
                    for user in layer.get("users", [])
                ]
            }
            for layer in result.get("schedule_layers", [])
        ]
    } 