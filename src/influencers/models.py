import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Influencer(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    gender: str | None = None
    approximate_age: int | None = None
    ethnicity_appearance: str | None = None
    hair_description: str | None = None
    skin_tone: str | None = None
    eye_color: str | None = None
    approximate_height_cm: int | None = None
    body_proportions: str | None = None
    facial_characteristics: str | None = None
    fashion_style: str | None = None
    negative_characteristics: str | None = None

    # Provider-specific identity data.
    identity_strategy: str = "face_reference"
    identity_embedding: str | None = None
    identity_metadata: str | None = None

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class InfluencerImage(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    influencer_id: str = Field(foreign_key="influencer.id", index=True)
    image_type: str  # face_reference | body_reference | identity_set
    file_path: str
    original_filename: str | None = None
    embedding: str | None = None
    metadata_json: str | None = None
    created_at: datetime = Field(default_factory=utcnow)