from fastapi import HTTPException, UploadFile
from sqlmodel import Session, select

from src.influencers.models import Influencer, InfluencerImage
from src.influencers.schemas import InfluencerCreate
from src.storage import storage


class InfluencerService:
    def create(self, session: Session, data: InfluencerCreate) -> Influencer:
        influencer = Influencer(**data.model_dump())
        session.add(influencer)
        session.commit()
        session.refresh(influencer)
        storage.influencer_dir(influencer.id)
        return influencer

    def get(self, session: Session, influencer_id: str) -> Influencer:
        influencer = session.get(Influencer, influencer_id)
        if not influencer:
            raise HTTPException(status_code=404, detail="Influencer not found")
        return influencer

    def list(self, session: Session) -> list[Influencer]:
        return list(session.exec(select(Influencer)).all())

    def add_identity_image(
        self,
        session: Session,
        influencer_id: str,
        image_type: str,
        upload: UploadFile,
    ) -> InfluencerImage:
        if image_type not in {"face_reference", "body_reference", "identity_set"}:
            raise HTTPException(status_code=400, detail="Invalid image type")

        self.get(session, influencer_id)
        content = upload.file.read()
        relative_path = storage.save_upload(
            influencer_id=influencer_id,
            category=f"identity/{'face_references' if image_type == 'face_reference' else 'body_references'}",
            filename=upload.filename or "reference.png",
            content=content,
        )

        image = InfluencerImage(
            influencer_id=influencer_id,
            image_type=image_type,
            file_path=relative_path,
            original_filename=upload.filename,
        )
        session.add(image)
        session.commit()
        session.refresh(image)
        return image

    def list_images(self, session: Session, influencer_id: str) -> list[InfluencerImage]:
        self.get(session, influencer_id)
        return list(
            session.exec(
                select(InfluencerImage).where(InfluencerImage.influencer_id == influencer_id)
            ).all()
        )


influencer_service = InfluencerService()