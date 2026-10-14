from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./ai_influencer.db"
    storage_root: str = "./storage"
    default_generation_provider: str = "flux_pulid_local"

    flux_pulid_model: str = "black-forest-labs/FLUX.1-dev"
    pu_lid_model_path: str = "./models/pulid_flux_v0.9.1.safetensors"

    identity_similarity_threshold: float = 0.80
    quality_score_threshold: float = 0.75
    pose_similarity_threshold: float = 0.80

    flux_kontext_api_key: str | None = None
    flux_kontext_endpoint: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()