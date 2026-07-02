from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CheckpointManager:
    def __init__(self, directory: str = ".checkpoints") -> None:
        self._dir = Path(directory)
        self._dir.mkdir(exist_ok=True)

    def save(self, run_id: str, state: dict, step: int) -> str:
        path = self._dir / f"{run_id}_{step:04d}.json"
        path.write_text(json.dumps({"run_id": run_id, "step": step, "state": state}, indent=2))
        return str(path)

    def load_latest(self, run_id: str) -> dict | None:
        files = sorted(self._dir.glob(f"{run_id}_*.json"))
        if not files:
            return None
        try:
            return json.loads(files[-1].read_text())
        except Exception:
            return None

    def list_runs(self) -> list[str]:
        runs = set()
        for f in self._dir.glob("*.json"):
            parts = f.stem.rsplit("_", 1)
            if len(parts) == 2:
                runs.add(parts[0])
        return sorted(runs)

    def delete(self, run_id: str) -> int:
        deleted = 0
        for f in list(self._dir.glob(f"{run_id}_*.json")):
            f.unlink()
            deleted += 1
        return deleted
