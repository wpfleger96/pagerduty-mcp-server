"""Parser for PagerDuty incidents."""

from typing import Any, Dict

from .parser_helpers import (
    parse_complex_item,
    parse_list_of_items,
    parse_sub_dictionary,
)


def parse_incident(*, result: Dict[str, Any]) -> Dict[str, Any]:
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
            - assignments (List[Dict]): List of assignments with assignee (containing id and summary) and timestamp
            - acknowledgements (List[Dict]): List of acknowledgements with acknowledger (containing id and summary) and timestamp
            - service (Dict): Service information with id
            - teams (List[Dict]): List of teams with id and summary
            - alert_counts (Dict): Counts of alerts
            - summary (str): Incident summary
            - description (str): Incident description
            - escalation_policy (Dict): Escalation policy information with id and summary
            - incident_key (str): Unique incident key
            - last_status_change_at (str): Last status change timestamp
            - last_status_change_by (Dict): User who last changed status with id and summary
            - body_details (Dict): Incident body details containing monitor information, query, and tags

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_incident = {}

    # Simple fields
    simple_fields = [
        "id",
        "incident_number",
        "title",
        "status",
        "urgency",
        "created_at",
        "updated_at",
        "resolved_at",
        "resolve_reason",
        "summary",
        "description",
        "incident_key",
        "last_status_change_at",
    ]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_incident[field] = value

    # Priority (can be a dict)
    priority_data = result.get("priority")
    if priority_data:
        parsed_incident["priority"] = priority_data

    # Alert Counts (can be a dict)
    alert_counts_data = result.get("alert_counts")
    if alert_counts_data:
        parsed_incident["alert_counts"] = alert_counts_data

    # Assignments
    parsed_assignments = parse_list_of_items(
        result.get("assignments"),
        lambda item: parse_complex_item(item, "assignee", ["id", "summary"]),
    )
    if parsed_assignments:
        parsed_incident["assignments"] = parsed_assignments

    # Acknowledgements
    parsed_acknowledgements = parse_list_of_items(
        result.get("acknowledgements"),
        lambda item: parse_complex_item(item, "acknowledger", ["id", "summary"]),
    )
    if parsed_acknowledgements:
        parsed_incident["acknowledgements"] = parsed_acknowledgements

    # Service
    parsed_service = parse_sub_dictionary(result.get("service"), ["id"])
    if parsed_service:
        parsed_incident["service"] = parsed_service

    # Teams
    parsed_teams = parse_list_of_items(
        result.get("teams"), lambda item: parse_sub_dictionary(item, ["id", "summary"])
    )
    if parsed_teams:
        parsed_incident["teams"] = parsed_teams

    # Escalation Policy
    parsed_escalation_policy = parse_sub_dictionary(
        result.get("escalation_policy"), ["id", "summary"]
    )
    if parsed_escalation_policy:
        parsed_incident["escalation_policy"] = parsed_escalation_policy

    # Last Status Change By
    parsed_lscb = parse_sub_dictionary(
        result.get("last_status_change_by"), ["id", "summary"]
    )
    if parsed_lscb:
        parsed_incident["last_status_change_by"] = parsed_lscb

    # Body Details
    body_payload = result.get("body", {}).get("details", {}).get("__pd_cef_payload")
    if isinstance(body_payload, dict):
        raw_body_details = body_payload.get("details")
        if (
            isinstance(raw_body_details, dict) and raw_body_details
        ):  # Check it's a non-empty dict
            keys_for_body_details = list(raw_body_details.keys())
            if "title" in keys_for_body_details:
                keys_for_body_details.remove("title")

            parsed_body_details = parse_sub_dictionary(
                raw_body_details, keys_for_body_details
            )
            if parsed_body_details:  # Add only if the processed dict is not empty
                parsed_incident["body_details"] = parsed_body_details

    return parsed_incident
