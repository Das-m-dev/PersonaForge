from dataclasses import asdict, dataclass, field

from src.config import settings


@dataclass
class QualityReport:
    identity_score: float | None = None
    pose_score: float | None = None
    clothing_score: float | None = None
    image_quality_score: float | None = None
    face_quality_score: float | None = None
    hand_anatomy_score: float | None = None
    artifacts_detected: list[str] = field(default_factory=list)
    passed: bool = False

    def to_dict(self):
        return asdict(self)


class IdentityVerifier:
    """
    Compares generated face embeddings with enrolled influencer embeddings.

    Phase 1 uses a neutral placeholder. Phase 2 should implement:
      - face detection
      - alignment
      - embedding extraction
      - cosine similarity against multiple enrolled references
    """

    def verify(self, generated_image_path, influencer_reference_paths) -> float | None:
        # TODO: replace with real embedding comparison.
        return None


class ImageQualityChecker:
    def check(
        self,
        generated_image_path,
        reference_analysis=None,
        identity_score=None,
        pose_score=None,
    ) -> QualityReport:
        report = QualityReport(
            identity_score=identity_score,
            pose_score=pose_score,
        )

        identity_ok = (
            identity_score is None
            or identity_score >= settings.identity_similarity_threshold
        )
        pose_ok = (
            pose_score is None
            or pose_score >= settings.pose_similarity_threshold
        )

        report.image_quality_score = 1.0  # Placeholder until real checks are added.
        report.passed = identity_ok and pose_ok
        return report


identity_verifier = IdentityVerifier()
image_quality_checker = ImageQualityChecker()