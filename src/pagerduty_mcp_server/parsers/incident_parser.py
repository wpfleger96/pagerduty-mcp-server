"""Parser for PagerDuty incidents."""

from typing import Dict, Any, Optional, List

def parse_incident(*,
                   result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw incident API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw incident API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The incident ID
            - incident_number (int): The incident number
            - title (str): The incident title
            - status (str): Current status of the incident
            - urgency (str): Urgency level of the incident
            - priority (dict): Priority information
            - created_at (str): Creation timestamp
            - updated_at (str): Last update timestamp
            - resolved_at (str): Resolution timestamp
            - resolve_reason (str): Reason for resolution
            - assignments (List[Dict]): List of assignments with assignee and timestamp
            - acknowledgements (List[Dict]): List of acknowledgements with acknowledger and timestamp
            - service (Dict): Service information with id and summary
            - teams (List[Dict]): List of teams with id and summary
            - alert_counts (Dict): Counts of alerts
            - auto_resolved (bool): Whether the incident was auto-resolved
            - summary (str): Incident summary
            - description (str): Incident description
            - escalation_policy (Dict): Escalation policy information
            - incident_key (str): Unique incident key
            - last_status_change_at (str): Last status change timestamp
            - last_status_change_by (Dict): User who last changed status
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary
    """

    if not result:
        return {}
    
    return {
        "id": result.get("id"),
        "incident_number": result.get("incident_number"),
        "title": result.get("title"),
        "status": result.get("status"),
        "urgency": result.get("urgency"),
        "priority": result.get("priority"),
        "created_at": result.get("created_at"),
        "updated_at": result.get("updated_at"),
        "resolved_at": result.get("resolved_at"),
        "resolve_reason": result.get("resolve_reason"),
        "assignments": [
            {
                "assignee": {
                    "id": assignment.get("assignee", {}).get("id"),
                    "summary": assignment.get("assignee", {}).get("summary")
                },
                "at": assignment.get("at")
            }
            for assignment in result.get("assignments", [])
        ],
        "acknowledgements": [
            {
                "acknowledger": {
                    "id": ack.get("acknowledger", {}).get("id"),
                    "summary": ack.get("acknowledger", {}).get("summary")
                },
                "at": ack.get("at")
            }
            for ack in result.get("acknowledgements", [])
        ],
        "service": {
            "id": result.get("service", {}).get("id"),
            "summary": result.get("service", {}).get("summary")
        },
        "teams": [
            {
                "id": team.get("id"),
                "summary": team.get("summary")
            }
            for team in result.get("teams", [])
        ],
        "alert_counts": result.get("alert_counts", {}),
        "auto_resolved": result.get("auto_resolved", False),
        "summary": result.get("summary"),
        "description": result.get("description"),
        "escalation_policy": {
            "id": result.get("escalation_policy", {}).get("id"),
            "summary": result.get("escalation_policy", {}).get("summary")
        },
        "incident_key": result.get("incident_key"),
        "last_status_change_at": result.get("last_status_change_at"),
        "last_status_change_by": {
            "id": result.get("last_status_change_by", {}).get("id"),
            "summary": result.get("last_status_change_by", {}).get("summary")
        }
    }
    