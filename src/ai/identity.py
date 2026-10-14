from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IdentityConditioning:
    strategy: str
    reference_paths: list[str]
    embedding: list[float] | None
    strength: float
    metadata: dict


class IdentityProvider(ABC):
    @abstractmethod
    def build_conditioning(
        self,
        influencer,
        reference_image_paths: list[str],
        strength: float = 0.8,
    ) -> IdentityConditioning:
        ...


class FaceReferenceProvider(IdentityProvider):
    """Uses curated face images directly as identity conditioning."""

    def build_conditioning(self, influencer, reference_image_paths, strength=0.8):
        return IdentityConditioning(
            strategy="face_reference",
            reference_paths=reference_image_paths,
            embedding=None,
            strength=strength,
            metadata={
                "influencer_id": influencer.id,
                "identity_strategy": influencer.identity_strategy,
            },
        )


class PuLIDIdentityProvider(IdentityProvider):
    """Tuning-free identity conditioning for FLUX-family models."""

    def build_conditioning(self, influencer, reference_image_paths, strength=0.8):
        if not reference_image_paths:
            raise ValueError("PuLID requires at least one face reference image")

        return IdentityConditioning(
            strategy="pulid_flux",
            reference_paths=reference_image_paths,
            embedding=None,
            strength=strength,
            metadata={
                "influencer_id": influencer.id,
                "pulid_model_path": influencer.identity_metadata,
            },
        )


class LoRAIdentityProvider(IdentityProvider):
    """Uses a per-influencer trained character LoRA."""

    def build_conditioning(self, influencer, reference_image_paths, strength=0.8):
        return IdentityConditioning(
            strategy="character_lora",
            reference_paths=reference_image_paths,
            embedding=None,
            strength=strength,
            metadata={
                "influencer_id": influencer.id,
                "lora_path": influencer.identity_metadata,
            },
        )


def get_identity_provider(strategy: str) -> IdentityProvider:
    providers = {
        "face_reference": FaceReferenceProvider(),
        "pulid_flux": PuLIDIdentityProvider(),
        "character_lora": LoRAIdentityProvider(),
    }
    if strategy not in providers:
        raise ValueError(f"Unknown identity strategy: {strategy}")
    return providers[strategy]