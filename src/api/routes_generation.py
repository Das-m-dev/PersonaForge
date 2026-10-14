from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.db import get_session
from src.generations.service import generation_service

router = APIRouter(tags=["generation"])


@router.post("/generate")
def generate(request: dict, session: Session = Depends(get_session)):
    return generation_service.create_generation(session, request)


@router.post("/generate/face-swap")
def face_swap(request: dict, session: Session = Depends(get_session)):
    request["mode"] = "face_swap"
    return generation_service.create_generation(session, request)


@router.post("/generate/body-replacement")
def body_replacement(request: dict, session: Session = Depends(get_session)):
    request["mode"] = "body_replacement"
    return generation_service.create_generation(session, request)


@router.post("/analyze-reference")
def analyze_reference(request: dict):
    from src.reference.analyzer import reference_analyzer
    from src.storage import storage

    path = storage.absolute_path(request["image_path"])
    return reference_analyzer.analyze(path).to_dict()


@router.get("/generations/{generation_id}")
def get_generation(generation_id: str, session: Session = Depends(get_session)):
    return generation_service.get(session, generation_id)


@router.get("/influencers/{influencer_id}/generations")
def list_generations(influencer_id: str, session: Session = Depends(get_session)):
    return generation_service.list_for_influencer(session, influencer_id)


@router.post("/generations/{generation_id}/regenerate")
def regenerate(generation_id: str, session: Session = Depends(get_session)):
    previous = generation_service.get(session, generation_id)
    request = {
        "influencer_id": previous.influencer_id,
        "mode": previous.mode,
        "prompt": previous.prompt,
        "negative_prompt": previous.negative_prompt,
        "reference_image": previous.reference_image,
    }
    return generation_service.create_generation(session, request)