from fastapi import FastAPI

from src.api.routes_generation import router as generation_router
from src.api.routes_influencers import router as influencer_router
from src.db import init_db
from src.ai.providers import flux_pulid_local  # noqa: F401
from src.ai.providers import flux_kontext_cloud  # noqa: F401

app = FastAPI(title="AI Influencer Studio", version="0.1.0")


@app.on_event("startup")
def startup():
    init_db()


app.include_router(influencer_router)
app.include_router(generation_router)