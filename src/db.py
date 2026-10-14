from sqlmodel import SQLModel, Session, create_engine

from src.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)


def init_db() -> None:
    # Import models so SQLModel registers tables.
    from src.influencers import models as _influencer_models  # noqa: F401
    from src.generations import models as _generation_models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session