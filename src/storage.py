import shutil
import uuid
from pathlib import Path

from src.config import settings


class ObjectStorage:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def influencer_dir(self, influencer_id: str) -> Path:
        path = self.root / "influencers" / influencer_id
        for sub in ("identity/face_references", "identity/body_references", "generated", "references", "masks", "metadata"):
            (path / sub).mkdir(parents=True, exist_ok=True)
        return path

    def save_upload(self, influencer_id: str, category: str, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix or ".png"
        relative = f"influencers/{influencer_id}/{category}/{uuid.uuid4().hex}{suffix}"
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return relative

    def save_generated(self, influencer_id: str, generation_id: str, content: bytes, extension: str = "png") -> str:
        relative = f"influencers/{influencer_id}/generated/{generation_id}.{extension}"
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return relative

    def save_mask(self, influencer_id: str, generation_id: str, mask_name: str, content: bytes) -> str:
        relative = f"influencers/{influencer_id}/masks/{generation_id}_{mask_name}.png"
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return relative

    def absolute_path(self, relative_path: str) -> Path:
        return self.root / relative_path

    def delete_influencer(self, influencer_id: str) -> None:
        path = self.root / "influencers" / influencer_id
        if path.exists():
            shutil.rmtree(path)


storage = ObjectStorage(settings.storage_root)