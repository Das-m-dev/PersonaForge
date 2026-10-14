from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from src.db import get_session
from src.influencers.schemas import InfluencerCreate, InfluencerImageRead, InfluencerRead
from src.influencers.service import influencer_service

router = APIRouter(prefix="/influencers", tags=["influencers"])


@router.post("", response_model=InfluencerRead)
def create_influencer(data: InfluencerCreate, session: Session = Depends(get_session)):
    return influencer_service.create(session, data)


@router.get("", response_model=list[InfluencerRead])
def list_influencers(session: Session = Depends(get_session)):
    return influencer_service.list(session)


@router.get("/{influencer_id}", response_model=InfluencerRead)
def get_influencer(influencer_id: str, session: Session = Depends(get_session)):
    return influencer_service.get(session, influencer_id)


@router.post("/{influencer_id}/identity-images", response_model=InfluencerImageRead)
def upload_identity_image(
    influencer_id: str,
    image_type: str,
    file: UploadFile,
    session: Session = Depends(get_session),
):
    return influencer_service.add_identity_image(session, influencer_id, image_type, file)


@router.get("/{influencer_id}/identity-images", response_model=list[InfluencerImageRead])
def list_identity_images(influencer_id: str, session: Session = Depends(get_session)):
    return influencer_service.list_images(session, influencer_id)