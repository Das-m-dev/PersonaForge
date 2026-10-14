from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class GenerationMode(str, Enum):
    NEW_IMAGE = "new_image"
    FACE_SWAP = "face_swap"
    BODY_REPLACEMENT = "body_replacement"


@dataclass
class GenerationRequest:
    influencer_id: str
    mode: GenerationMode
    prompt: str
    negative_prompt: str = ""
    aspect_ratio: str = "4:5"
    reference_image_path: str | None = None
    identity_strength: float = 0.8
    pose_strength: float = 0.8
    reference_strength: float = 0.8
    preserve_clothing: bool = False
    preserve_background: bool = False
    preserve_lighting: bool = False
    seed: int | None = None
    width: int = 1024
    height: int = 1280
    extra: dict = field(default_factory=dict)


@dataclass
class GenerationResult:
    image_bytes: bytes
    provider: str
    model: str
    model_version: str
    seed: int
    parameters: dict


class ImageGenerationProvider(ABC):
    name: str
    model: str
    model_version: str

    @abstractmethod
    def generate(self, request: GenerationRequest, identity, reference_analysis) -> GenerationResult:
        ...

    @abstractmethod
    def edit(self, request: GenerationRequest, identity, reference_analysis) -> GenerationResult:
        ...

    @abstractmethod
    def inpaint(
        self,
        request: GenerationRequest,
        identity,
        reference_analysis,
        mask_bytes: bytes,
    ) -> GenerationResult:
        ...


class ProviderRegistry:
    def __init__(self):
        self._providers = {}

    def register(self, provider: ImageGenerationProvider):
        self._providers[provider.name] = provider

    def get(self, name: str) -> ImageGenerationProvider:
        if name not in self._providers:
            raise ValueError(f"Generation provider not registered: {name}")
        return self._providers[name]


provider_registry = ProviderRegistry()