from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorkflowCheckpoint:
    checkpoint_id: str
    workflow_id: str
    step: str
    state: dict[str, Any]
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "checkpoint_id": self.checkpoint_id,
            "workflow_id": self.workflow_id,
            "step": self.step,
            "state": self.state,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowCheckpoint":
        return cls(
            checkpoint_id=data["checkpoint_id"],
            workflow_id=data["workflow_id"],
            step=data["step"],
            state=data["state"],
            created_at=data.get("created_at", time.time()),
        )


class WorkflowCheckpointer:
    def __init__(self, storage_dir: str = ".checkpoints") -> None:
        self._dir = Path(storage_dir)
        self._dir.mkdir(exist_ok=True)

    def _path(self, checkpoint_id: str) -> Path:
        return self._dir / f"{checkpoint_id}.json"

    def save(self, checkpoint: WorkflowCheckpoint) -> None:
        self._path(checkpoint.checkpoint_id).write_text(
            json.dumps(checkpoint.to_dict(), indent=2), encoding="utf-8"
        )

    def load(self, checkpoint_id: str) -> WorkflowCheckpoint | None:
        p = self._path(checkpoint_id)
        if not p.exists():
            return None
        return WorkflowCheckpoint.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def delete(self, checkpoint_id: str) -> bool:
        p = self._path(checkpoint_id)
        if p.exists():
            p.unlink()
            return True
        return False

    def list_for_workflow(self, workflow_id: str) -> list[WorkflowCheckpoint]:
        checkpoints = []
        for f in self._dir.glob("*.json"):
            try:
                cp = WorkflowCheckpoint.from_dict(json.loads(f.read_text(encoding="utf-8")))
                if cp.workflow_id == workflow_id:
                    checkpoints.append(cp)
            except (json.JSONDecodeError, KeyError):
                continue
        return sorted(checkpoints, key=lambda c: c.created_at)

    def latest(self, workflow_id: str) -> WorkflowCheckpoint | None:
        cps = self.list_for_workflow(workflow_id)
        return cps[-1] if cps else None
