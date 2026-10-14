import json

from fastapi import HTTPException
from sqlmodel import Session, select

from src.ai.generation import GenerationMode, GenerationRequest, provider_registry
from src.ai.identity import get_identity_provider
from src.ai.quality import identity_verifier, image_quality_checker
from src.config import settings
from src.generations.models import Generation
from src.influencers.service import influencer_service
from src.reference.analyzer import reference_analyzer
from src.storage import storage


class GenerationService:
    def create_generation(self, session: Session, request_data: dict) -> Generation:
        influencer = influencer_service.get(session, request_data["influencer_id"])
        mode = GenerationMode(request_data["mode"])

        reference_path = request_data.get("reference_image")
        if mode != GenerationMode.NEW_IMAGE and not reference_path:
            raise HTTPException(status_code=400, detail="Reference image required for this mode")

        generation = Generation(
            influencer_id=influencer.id,
            mode=mode.value,
            prompt=request_data.get("prompt", ""),
            negative_prompt=request_data.get("negative_prompt", ""),
            reference_image=reference_path,
            status="processing",
        )
        session.add(generation)
        session.commit()
        session.refresh(generation)

        try:
            analysis = reference_analyzer.analyze(
                storage.absolute_path(reference_path)
            ) if reference_path else None

            identity_provider = get_identity_provider(
                request_data.get("identity_strategy", influencer.identity_strategy)
            )
            identity = identity_provider.build_conditioning(
                influencer=influencer,
                reference_image_paths=self._face_references(session, influencer.id),
                strength=request_data.get("identity_strength", 0.8),
            )

            provider = provider_registry.get(
                request_data.get("provider", settings.default_generation_provider)
            )
            generation_request = GenerationRequest(
                influencer_id=influencer.id,
                mode=mode,
                prompt=request_data.get("prompt", ""),
                negative_prompt=request_data.get("negative_prompt", ""),
                aspect_ratio=request_data.get("aspect_ratio", "4:5"),
                reference_image_path=reference_path,
                identity_strength=request_data.get("identity_strength", 0.8),
                pose_strength=request_data.get("pose_strength", 0.8),
                reference_strength=request_data.get("reference_strength", 0.8),
                preserve_clothing=request_data.get("preserve_clothing", False),
                preserve_background=request_data.get("preserve_background", False),
                preserve_lighting=request_data.get("preserve_lighting", False),
                seed=request_data.get("seed"),
            )

            if mode == GenerationMode.NEW_IMAGE:
                result = provider.generate(generation_request, identity, analysis.to_dict() if analysis else {})
            else:
                result = provider.edit(generation_request, identity, analysis.to_dict() if analysis else {})

            generated_path = storage.save_generated(
                influencer_id=influencer.id,
                generation_id=generation.id,
                content=result.image_bytes,
            )

            identity_score = identity_verifier.verify(
                storage.absolute_path(generated_path),
                self._face_reference_absolute_paths(session, influencer.id),
            )
            quality = image_quality_checker.check(
                generated_image_path=storage.absolute_path(generated_path),
                reference_analysis=analysis.to_dict() if analysis else None,
                identity_score=identity_score,
            )

            generation.generated_image = generated_path
            generation.provider = result.provider
            generation.model = result.model
            generation.model_version = result.model_version
            generation.seed = result.seed
            generation.generation_parameters = json.dumps(result.parameters, default=str)
            generation.reference_analysis = json.dumps(analysis.to_dict(), default=str) if analysis else None
            generation.identity_score = identity_score
            generation.pose_score = quality.pose_score
            generation.quality_score = quality.image_quality_score
            generation.passed = quality.passed
            generation.status = "completed" if quality.passed else "needs_review"
            session.commit()
            session.refresh(generation)
            return generation

        except Exception as exc:
            generation.status = "failed"
            generation.error_message = str(exc)
            session.commit()
            session.refresh(generation)
            raise

    def get(self, session: Session, generation_id: str) -> Generation:
        generation = session.get(Generation, generation_id)
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        return generation

    def list_for_influencer(self, session: Session, influencer_id: str) -> list[Generation]:
        influencer_service.get(session, influencer_id)
        return list(
            session.exec(
                select(Generation).where(Generation.influencer_id == influencer_id)
            ).all()
        )

    def _face_references(self, session: Session, influencer_id: str) -> list[str]:
        return [
            image.file_path
            for image in influencer_service.list_images(session, influencer_id)
            if image.image_type in {"face_reference", "identity_set"}
        ]

    def _face_reference_absolute_paths(self, session: Session, influencer_id: str) -> list[str]:
        return [
            str(storage.absolute_path(path))
            for path in self._face_references(session, influencer_id)
        ]


generation_service = GenerationService()