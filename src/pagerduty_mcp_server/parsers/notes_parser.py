"""Parser for PagerDuty note objects."""

from typing import Optional


def parse_note(note_data: Optional[dict]) -> Optional[dict]:
    """Parse a PagerDuty note object into a simplified format.

    Args:
        note_data: Raw note data from the PagerDuty API

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The note ID
            - content (str): The content of the note
            - created_at (str): Creation timestamp
            - user (Dict): Information about the user who created the note:
                - id (str): User ID
                - name (str): User name (from summary field)
            - channel (Dict): Information about the channel:
                - summary (str): Channel summary

        Returns None if input is None or empty
    """
    if not note_data:
        return None

    return {
        "id": note_data.get("id"),
        "content": note_data.get("content"),
        "created_at": note_data.get("created_at"),
        "user": {
            "id": note_data.get("user", {}).get("id"),
            "name": note_data.get("user", {}).get("summary"),
        },
        "channel": {
            "summary": note_data.get("channel", {}).get("summary"),
        },
    }
