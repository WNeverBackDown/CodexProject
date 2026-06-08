from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("_") or "run"


@dataclass(frozen=True)
class ArtifactStore:
    root: Path

    @classmethod
    def create(cls, root: str | Path, name: str = "manual") -> "ArtifactStore":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path(root).resolve() / f"{timestamp}_{safe_name(name)}"
        path.mkdir(parents=True, exist_ok=True)
        return cls(root=path)

    def write_text(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path
