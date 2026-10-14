from datetime import datetime

from pydantic import BaseModel, Field


class InfluencerCreate(BaseModel):
    name: str
    gender: str | None = None
    approximate_age: int | None = Field(default=None, ge=18, le=100)
    ethnicity_appearance: str | None = None
    hair_description: str | None = None
    skin_tone: str | None = None
    eye_color: str | None = None
    approximate_height_cm: int | None = None
    body_proportions: str | None = None
    facial_characteristics: str | None = None
    fashion_style: str | None = None
    negative_characteristics: str | None = None
    identity_strategy: str = "face_reference"


class InfluencerRead(InfluencerCreate):
    id: str
    created_at: datetime
    updated_at: datetime


class InfluencerImageRead(BaseModel):
    id: str
    influencer_id: str
    image_type: str
    file_path: str
    original_filename: str | None
    created_at: datetime