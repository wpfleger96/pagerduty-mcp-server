"""Pydantic models for PagerDuty Notes."""

from pydantic import ConfigDict, Field

from .common import PagerDutyBaseModel


class NoteUser(PagerDutyBaseModel):
    """A user who created a note."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: str
    name: str | None = Field(None, alias="summary", serialization_alias="name")


class NoteChannel(PagerDutyBaseModel):
    """A channel where a note was created."""

    summary: str | None = None


class Note(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Note."""

    # Required field - always present
    id: str

    # Core fields - present in full API responses but may be missing in simplified contexts
    content: str | None = None
    created_at: str | None = None
    user: NoteUser | None = None
    channel: NoteChannel | None = None
