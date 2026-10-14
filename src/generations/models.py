import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Generation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    influencer_id: str = Field(foreign_key="influencer.id", index=True)
    mode: str = Field(index=True)
    prompt: str
    negative_prompt: str | None = None
    reference_image: str | None = None
    generated_image: str | None = None
    provider: str | None = None
    model: str | None = None
    model_version: str | None = None
    seed: int | None = None
    generation_parameters: str | None = None
    reference_analysis: str | None = None
    masks: str | None = None
    identity_score: float | None = None
    pose_score: float | None = None
    quality_score: float | None = None
    passed: bool | None = None
    status: str = Field(default="pending", index=True)
    error_message: str | None = None
    created_at: datetime = Field(default_factory=utcnow)