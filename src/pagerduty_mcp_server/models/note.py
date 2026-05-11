"""Pydantic models for PagerDuty Notes."""

from typing import Optional

from pydantic import ConfigDict, Field

from .common import PagerDutyBaseModel


class NoteUser(PagerDutyBaseModel):
    """A user who created a note."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: str
    name: Optional[str] = Field(None, alias="summary", serialization_alias="name")


class NoteChannel(PagerDutyBaseModel):
    """A channel where a note was created."""

    summary: Optional[str] = None


class Note(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Note."""

    # Required field - always present
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    content: Optional[str] = None
    created_at: Optional[str] = None
    user: Optional[NoteUser] = None
    channel: Optional[NoteChannel] = None
