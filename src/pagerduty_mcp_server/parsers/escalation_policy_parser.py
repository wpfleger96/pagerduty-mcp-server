"""Parser for PagerDuty escalation policies."""

from typing import Dict, Any

def parse_escalation_policy(*,
                            result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw escalation policy API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw escalation policy API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The policy ID
            - html_url (str): URL to view the policy in PagerDuty
            - summary (str): The policy summary
            - name (str): The policy name
            - escalation_rules (List[Dict]): List of escalation rules, each containing:
                - id (str): Rule ID
                - escalation_delay_in_minutes (int): Delay before escalation
                - targets (List[Dict]): List of targets with id, summary, and html_url
            - services (List[Dict]): List of services with id, summary, and html_url
            - num_loops (int): Number of times to loop through the policy (defaults to 1)
            - teams (List[Dict]): List of teams with id, summary, and html_url
            - description (str): Policy description
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary.
        The num_loops field defaults to 1 if not specified in the input.
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "html_url": result.get("html_url"),
        "summary": result.get("summary"),
        "name": result.get("name"),
        "escalation_rules": [
            {
                "id": rule.get("id"),
                "escalation_delay_in_minutes": rule.get("escalation_delay_in_minutes"),
                "targets": [
                    {
                        "id": target.get("id"),
                        "summary": target.get("summary"),
                        "html_url": target.get("html_url")
                    }
                    for target in rule.get("targets", [])
                ]
            }
            for rule in result.get("escalation_rules", [])
        ],
        "services": [
            {
                "id": service.get("id"),
                "summary": service.get("summary"),
                "html_url": service.get("html_url")
            }
            for service in result.get("services", [])
        ],
        "num_loops": result.get("num_loops", 1),  # Default to 1 loop if not specified
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary"),
                "html_url": team.get("html_url")
            }
            for team in result.get("teams", [])
        ],
        "description": result.get("description")
    }

    
