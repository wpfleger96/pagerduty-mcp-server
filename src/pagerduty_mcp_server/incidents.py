"""PagerDuty incident operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .client import create_client
from .parsers import parse_incident
from .parsers.notes_parser import parse_note

logger = logging.getLogger(__name__)

INCIDENTS_URL = "/incidents"

VALID_STATUSES = ["triggered", "acknowledged", "resolved"]
DEFAULT_STATUSES = ["triggered", "acknowledged", "resolved"]
VALID_URGENCIES = ["high", "low"]
DEFAULT_URGENCIES = ["high", "low"]

AUTORESOLVE_TYPE = "service_reference"

"""
Incidents API Helpers
"""


def list_incidents(
    *,
    service_ids: Optional[List[str]] = None,
    team_ids: Optional[List[str]] = None,
    statuses: Optional[List[str]] = None,
    urgencies: Optional[List[str]] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """List PagerDuty incidents based on specified filters. Exposed in `get_incidents`.

    Args:
        service_ids (List[str]): List of PagerDuty service IDs to filter by (optional)
        team_ids (List[str]): List of PagerDuty team IDs to filter by (optional)
        statuses (List[str]): List of status values to filter by (optional). Valid values are:
            - 'triggered' - The incident is currently active (included by default)
            - 'acknowledged' - The incident has been acknowledged by a user (included by default)
            - 'resolved' - The incident has been resolved (included by default)
            Defaults to ['triggered', 'acknowledged', 'resolved'] if not specified.
        urgencies (List[str]): List of urgency values to filter by (optional). Valid values are:
            - 'high' - High urgency incidents (included by default)
            - 'low' - Low urgency incidents (included by default)
            Defaults to ['high', 'low'] if not specified.
        since (str): Start of date range in ISO8601 format (optional). Default is 1 month ago
        until (str): End of date range in ISO8601 format (optional). Default is now
        limit (int): Limit the number of results returned (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of incidents with additional metadata about status counts and autoresolve counts.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """
    pd_client = create_client()

    if statuses is None:
        statuses = DEFAULT_STATUSES
    else:
        invalid_statuses = [s for s in statuses if s not in VALID_STATUSES]
        if invalid_statuses:
            raise ValueError(
                f"Invalid status values: {invalid_statuses}. Valid values are: {VALID_STATUSES}"
            )

    if urgencies is None:
        urgencies = DEFAULT_URGENCIES
    else:
        invalid_urgencies = [u for u in urgencies if u not in VALID_URGENCIES]
        if invalid_urgencies:
            raise ValueError(
                f"Invalid urgency values: {invalid_urgencies}. Valid values are: {VALID_URGENCIES}"
            )

    params = {"statuses": statuses, "urgencies": urgencies}
    if service_ids:
        params["service_ids"] = service_ids
    if team_ids:
        params["team_ids"] = team_ids
    if since is not None:
        utils.validate_iso8601_timestamp(since, "since")
        params["since"] = since
    if until is not None:
        utils.validate_iso8601_timestamp(until, "until")
        params["until"] = until
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(INCIDENTS_URL, params=params)
        metadata = _calculate_incident_metadata(response)
        parsed_response = [parse_incident(result=result) for result in response]

        return utils.api_response_handler(
            results=parsed_response,
            resource_name="incidents",
            additional_metadata=metadata,
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_incident(
    *,
    incident_id: str,
    include_past_incidents: Optional[bool] = False,
    include_related_incidents: Optional[bool] = False,
    include_notes: Optional[bool] = False,
) -> Dict[str, Any]:
    """Get detailed information about a given incident. Exposed as MCP server tool.

    Args:
        incident_id (str): The ID or number of the incident to get
        include_past_incidents (Optional[bool]): If True, includes similar past incidents. Defaults to False.
        include_related_incidents (Optional[bool]): If True, includes related incidents. Defaults to False.
        include_notes (Optional[bool]): If True, includes notes for the incident. Defaults to False.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single incident in the standard format.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not incident_id:
        raise ValueError("incident_id cannot be empty")

    pd_client = create_client()
    params = {"include[]": "body"}

    try:
        incident_metadata = {}

        response = pd_client.jget(f"{INCIDENTS_URL}/{incident_id}", params=params)
        try:
            incident_data = response["incident"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch or process incident {incident_id}: 'incident'"
            )

        parsed_main_incident = parse_incident(result=incident_data)

        if include_past_incidents:
            try:
                past_incidents_response = _list_past_incidents(incident_id=incident_id)
                if past_incidents_response and past_incidents_response.get("incidents"):
                    parsed_main_incident["past_incidents"] = past_incidents_response[
                        "incidents"
                    ]

                if parsed_main_incident.get("past_incidents"):
                    incident_metadata["past_incidents_count"] = len(
                        parsed_main_incident["past_incidents"]
                    )
            except Exception as e_past:
                logger.error(
                    f"Error fetching past incidents for {incident_id}: {e_past}"
                )

        if include_related_incidents:
            try:
                related_incidents_response = _list_related_incidents(
                    incident_id=incident_id
                )
                if related_incidents_response and related_incidents_response.get(
                    "incidents"
                ):
                    parsed_main_incident["related_incidents"] = (
                        related_incidents_response["incidents"]
                    )

                if parsed_main_incident.get("related_incidents"):
                    incident_metadata["related_incidents_count"] = len(
                        parsed_main_incident["related_incidents"]
                    )
            except Exception as e_related:
                logger.error(
                    f"Error fetching related incidents for {incident_id}: {e_related}"
                )

        if include_notes:
            try:
                notes_response = _list_notes(incident_id=incident_id)
                if notes_response and notes_response.get("notes"):
                    parsed_main_incident["notes"] = notes_response["notes"]

                if parsed_main_incident.get("notes"):
                    incident_metadata["notes_count"] = len(
                        parsed_main_incident["notes"]
                    )
            except Exception as e_notes:
                logger.error(
                    f"Error fetching notes for incident {incident_id}: {e_notes}"
                )

        return utils.api_response_handler(
            results=parsed_main_incident,
            resource_name="incident",
            additional_metadata=incident_metadata,
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Incidents Private Helpers
"""


def _list_past_incidents(
    *, incident_id: str, limit: Optional[int] = None, total: Optional[bool] = None
) -> Dict[str, Any]:
    """List incidents from the past 6 months that are similar to the input incident, and were generated on the same service as the parent incident.

    Args:
        incident_id (str): The ID or number of the incident to find similar incidents for
        limit (int): The maximum number of past incidents to return (optional). This parameter is passed
            directly to the PagerDuty API. Default in the API is 5.
        total (bool): Whether to return the total number of incidents that match the criteria (optional).
            This parameter is passed directly to the PagerDuty API. Default is False.

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of past incidents with similarity scores.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not incident_id:
        raise ValueError("incident_id cannot be empty")

    pd_client = create_client()

    params = {"limit": limit, "total": total}
    try:
        response = pd_client.jget(
            f"{INCIDENTS_URL}/{incident_id}/past_incidents", params=params
        )
        try:
            past_incidents = response["past_incidents"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch past incidents for {incident_id}: Response missing 'past_incidents' field"
            )

        parsed_response = [
            {
                **parse_incident(result=item.get("incident", {})),
                "similarity_score": item.get("score", 0.0),
            }
            for item in past_incidents
        ]
        parsed_response.sort(key=lambda x: x["similarity_score"], reverse=True)

        return utils.api_response_handler(
            results=parsed_response, resource_name="incidents"
        )
    except Exception as e:
        utils.handle_api_error(e)


def _list_related_incidents(*, incident_id: str) -> Dict[str, Any]:
    """List the 20 most recent related incidents that are impacting other services and responders.

    Args:
        incident_id (str): The ID or number of the incident to get related incidents for

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of related incidents with relationship metadata.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not incident_id:
        raise ValueError("incident_id cannot be empty")

    pd_client = create_client()

    try:
        response = pd_client.jget(f"{INCIDENTS_URL}/{incident_id}/related_incidents")
        try:
            related_incidents = response["related_incidents"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch related incidents for {incident_id}: Response missing 'related_incidents' field"
            )

        parsed_response = [
            {
                **parse_incident(result=item["incident"]),
                "relationship_type": item["relationships"][0]["type"]
                if item["relationships"]
                else None,
                "relationship_metadata": item["relationships"][0]["metadata"]
                if item["relationships"]
                else None,
            }
            for item in related_incidents
        ]

        return utils.api_response_handler(
            results=parsed_response, resource_name="incidents"
        )
    except Exception as e:
        utils.handle_api_error(e)


def _list_notes(*, incident_id: str) -> Dict[str, Any]:
    """List notes for a PagerDuty incident. Exposed as MCP server tool.

    Args:
        incident_id (str): The ID or number of the incident to get notes for

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of notes with user and channel information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not incident_id:
        raise ValueError("incident_id cannot be empty")

    pd_client = create_client()

    try:
        response = pd_client.jget(f"{INCIDENTS_URL}/{incident_id}/notes")
        try:
            notes = response["notes"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch notes for incident {incident_id}: Response missing 'notes' field"
            )

        parsed_response = [parse_note(note) for note in notes]

        return utils.api_response_handler(
            results=parsed_response, resource_name="notes"
        )
    except Exception as e:
        utils.handle_api_error(e)


def _count_incident_statuses(incidents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count incidents by status. Internal helper function.

    Args:
        incidents (List[Dict[str, Any]]): List of incident objects

    Returns:
        Dict[str, int]: Dictionary mapping status to count
    """
    status_counts = {}
    for incident in incidents:
        status = incident.get("status")
        if status in VALID_STATUSES:
            status_counts[status] = status_counts.get(status, 0) + 1
    return status_counts


def _count_autoresolved_incidents(incidents: List[Dict[str, Any]]) -> int:
    """Count incidents that were auto-resolved. Internal helper function.

    Args:
        incidents (List[Dict[str, Any]]): List of incident objects

    Returns:
        int: Number of auto-resolved incidents
    """
    return sum(
        1
        for incident in incidents
        if (
            incident.get("status") == "resolved"
            and incident.get("last_status_change_by", {}).get("type", "")
            == AUTORESOLVE_TYPE
        )
    )


def _count_no_data_incidents(incidents: List[Dict[str, Any]]) -> int:
    """Count incidents that are "no data" incidents. Internal helper function.

    Args:
        incidents (List[Dict[str, Any]]): List of incident objects

    Returns:
        int: Number of incidents with titles starting with "No Data:"
    """
    return sum(
        1 for incident in incidents if incident.get("title", "").startswith("No Data:")
    )


def _calculate_incident_metadata(incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate additional metadata for incidents including status counts and autoresolve count. Internal helper function.

    Args:
        incidents (List[Dict[str, Any]]): List of incident objects

    Returns:
        Dict[str, Any]: Dictionary containing:
            - status_counts (Dict[str, int]): Dictionary mapping each status to its count
            - autoresolve_count (int): Number of incidents that were auto-resolved
                (status='resolved' and last_status_change_by.type='service_reference')
            - no_data_count (int): Number of incidents generated by "No Data" events
    """
    if not incidents:
        return {
            "status_counts": {status: 0 for status in VALID_STATUSES},
            "autoresolve_count": 0,
            "no_data_count": 0,
        }

    status_counts = _count_incident_statuses(incidents)
    autoresolve_count = _count_autoresolved_incidents(incidents)
    no_data_count = _count_no_data_incidents(incidents)

    return {
        "status_counts": {
            status: status_counts.get(status, 0) for status in VALID_STATUSES
        },
        "autoresolve_count": autoresolve_count,
        "no_data_count": no_data_count,
    }
