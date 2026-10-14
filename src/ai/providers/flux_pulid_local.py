import random
from pathlib import Path

from src.ai.generation import (
    GenerationMode,
    GenerationRequest,
    GenerationResult,
    ImageGenerationProvider,
)
from src.config import settings


class FluxPuLIDLocalProvider(ImageGenerationProvider):
    """
    Local FLUX.1-dev + PuLID provider.

    This class is deliberately a stable integration boundary. In Phase 1 it can run
    against a local ComfyUI worker or a diffusers implementation. The application
    does not need to know which runtime is used.
    """

    name = "flux_pulid_local"
    model = settings.flux_pulid_model
    model_version = "flux.1-dev + pulid-flux-v0.9.1"

    def generate(self, request, identity, reference_analysis):
        seed = request.seed if request.seed is not None else random.randint(0, 2**32 - 1)

        # TODO Phase 2: call local FLUX/PuLID runtime.
        # Recommended interface: submit job to a ComfyUI queue or local inference worker.
        payload = {
            "mode": request.mode.value,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "identity_strategy": identity.strategy,
            "identity_references": identity.reference_paths,
            "identity_strength": identity.strength,
            "width": request.width,
            "height": request.height,
            "seed": seed,
        }

        return GenerationResult(
            image_bytes=self._placeholder_image(),
            provider=self.name,
            model=self.model,
            model_version=self.model_version,
            seed=seed,
            parameters=payload,
        )

    def edit(self, request, identity, reference_analysis):
        if not request.reference_image_path:
            raise ValueError("Reference image is required for editing")

        seed = request.seed if request.seed is not None else random.randint(0, 2**32 - 1)

        instruction = self._build_edit_instruction(request, reference_analysis)

        return GenerationResult(
            image_bytes=self._placeholder_image(),
            provider=self.name,
            model=self.model,
            model_version=self.model_version,
            seed=seed,
            parameters={
                "mode": request.mode.value,
                "edit_instruction": instruction,
                "reference_image": request.reference_image_path,
                "identity_strategy": identity.strategy,
                "identity_strength": identity.strength,
                "pose_strength": request.pose_strength,
                "reference_strength": request.reference_strength,
                "seed": seed,
            },
        )

    def inpaint(self, request, identity, reference_analysis, mask_bytes):
        if not request.reference_image_path:
            raise ValueError("Reference image is required for inpainting")

        seed = request.seed if request.seed is not None else random.randint(0, 2**32 - 1)

        return GenerationResult(
            image_bytes=self._placeholder_image(),
            provider=self.name,
            model=self.model,
            model_version=self.model_version,
            seed=seed,
            parameters={
                "mode": request.mode.value,
                "operation": "masked_inpaint",
                "reference_image": request.reference_image_path,
                "mask_bytes": len(mask_bytes),
                "identity_strategy": identity.strategy,
                "pose": reference_analysis.get("pose"),
                "clothing": reference_analysis.get("clothing"),
                "scene": reference_analysis.get("scene"),
                "seed": seed,
            },
        )

    def _build_edit_instruction(self, request, reference_analysis):
        if request.mode == GenerationMode.FACE_SWAP:
            return (
                "Replace only the person's facial identity with the provided influencer "
                "face reference. Preserve head orientation, expression, pose, body, clothing, "
                "background, camera angle, framing, lighting, shadows, and skin-tone integration."
            )

        if request.mode == GenerationMode.BODY_REPLACEMENT:
            clothing = "the same outfit, garment colors, garment structure, and accessories"
            pose = "the same body pose, limb positions, hand positions, and body proportions"
            scene = "the same camera angle, framing, environment, background, and lighting"

            return (
                f"Replace the person with the provided influencer identity while preserving "
                f"{clothing}, {pose}, and {scene}. Do not alter the background or unrelated objects."
            )

        return request.prompt

    def _placeholder_image(self) -> bytes:
        # Phase 1 returns a tiny valid PNG so API/storage flows can be tested.
        return bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001080600000"
            "01f15c4890000000d49444154789c626001000000ffff030000060005"
            "57bfabd40000000049454e44ae426082"
        )


provider_registry.register(FluxPuLIDLocalProvider())