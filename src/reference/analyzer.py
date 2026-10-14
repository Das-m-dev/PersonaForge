from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class FaceAnalysis:
    face_box: list[int] | None = None
    landmarks: list[list[float]] = field(default_factory=list)
    head_yaw: float | None = None
    head_pitch: float | None = None
    head_roll: float | None = None
    occlusions: list[str] = field(default_factory=list)


@dataclass
class PoseAnalysis:
    keypoints: dict[str, list[float]] = field(default_factory=dict)
    body_orientation: str | None = None
    confidence: float | None = None


@dataclass
class ClothingAnalysis:
    categories: list[str] = field(default_factory=list)
    dominant_colors: list[str] = field(default_factory=list)
    garment_description: str | None = None
    mask_path: str | None = None


@dataclass
class SceneAnalysis:
    environment: str | None = None
    location_type: str | None = None
    background_description: str | None = None
    lighting: str | None = None


@dataclass
class CompositionAnalysis:
    width: int | None = None
    height: int | None = None
    subject_position: str | None = None
    camera_angle: str | None = None
    camera_distance: str | None = None


@dataclass
class ReferenceAnalysis:
    face: FaceAnalysis
    pose: PoseAnalysis
    clothing: ClothingAnalysis
    scene: SceneAnalysis
    composition: CompositionAnalysis
    masks: dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


class ReferenceAnalyzer:
    """
    Phase 1 interface and structured output contract.

    Phase 3/4 implementations should plug in:
      - face detection / landmarks
      - SAM 2 or equivalent segmentation
      - DWPose / OpenPose-style pose estimation
      - clothing segmentation / captioning
      - scene and composition classification
    """

    def analyze(self, image_path: str | Path) -> ReferenceAnalysis:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        return ReferenceAnalysis(
            face=FaceAnalysis(),
            pose=PoseAnalysis(),
            clothing=ClothingAnalysis(),
            scene=SceneAnalysis(),
            composition=CompositionAnalysis(),
        )


reference_analyzer = ReferenceAnalyzer()