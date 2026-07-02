from __future__ import annotations

import hashlib
import json
from pathlib import Path


class SessionStore:
    """Persist agent sessions as JSON for resumable research conversations."""

    def __init__(self, directory: str = ".sessions") -> None:
        self._dir = Path(directory)
        self._dir.mkdir(exist_ok=True)

    def _path(self, session_id: str) -> Path:
        safe = hashlib.md5(session_id.encode()).hexdigest()
        return self._dir / f"{safe}.json"

    def save(self, session_id: str, data: dict) -> None:
        self._path(session_id).write_text(json.dumps(data, indent=2))

    def load(self, session_id: str) -> dict | None:
        p = self._path(session_id)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text())
        except Exception:
            return None

    def delete(self, session_id: str) -> bool:
        p = self._path(session_id)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_sessions(self) -> list[str]:
        return [f.stem for f in self._dir.glob("*.json")]
