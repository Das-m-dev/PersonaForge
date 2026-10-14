import random

import httpx

from src.ai.generation import GenerationRequest, GenerationResult, ImageGenerationProvider
from src.config import settings


class FluxKontextCloudProvider(ImageGenerationProvider):
    """
    Optional cloud fallback for reference-guided edits.

    FLUX Kontext accepts an input image plus a natural-language edit instruction and is
    designed for targeted edits and character preservation. Use it when local GPU
    throughput is insufficient or as an A/B provider.
    """

    name = "flux_kontext_cloud"
    model = "FLUX.1 Kontext [pro]"
    model_version = "pro"

    def generate(self, request, identity, reference_analysis):
        raise NotImplementedError("Use local provider for text-to-image in Phase 1")

    def edit(self, request, identity, reference_analysis):
        if not settings.flux_kontext_api_key:
            raise RuntimeError("FLUX Kontext API key is not configured")

        seed = request.seed if request.seed is not None else random.randint(0, 2**32 - 1)

        # TODO: adapt to the exact provider request schema.
        response = httpx.post(
            settings.flux_kontext_endpoint or "",
            headers={"Authorization": f"Bearer {settings.flux_kontext_api_key}"},
            json={
                "image_url": request.reference_image_path,
                "prompt": request.prompt,
                "seed": seed,
                "aspect_ratio": request.aspect_ratio,
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        return GenerationResult(
            image_bytes=httpx.get(data["image_url"]).content,
            provider=self.name,
            model=self.model,
            model_version=self.model_version,
            seed=seed,
            parameters=data,
        )

    def inpaint(self, request, identity, reference_analysis, mask_bytes):
        raise NotImplementedError("Add provider-specific masked-edit support when needed")


# Register only when configured.
if settings.flux_kontext_api_key:
    from src.ai.generation import provider_registry

    provider_registry.register(FluxKontextCloudProvider())