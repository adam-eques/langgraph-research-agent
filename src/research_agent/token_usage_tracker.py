from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TokenUsageRecord:
    session_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp,
        }


class TokenUsageTracker:
    def __init__(self, log_path: str | None = None) -> None:
        self._records: list[TokenUsageRecord] = []
        self._log_path = Path(log_path) if log_path else None

    def record(
        self,
        session_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        metadata: dict | None = None,
    ) -> TokenUsageRecord:
        rec = TokenUsageRecord(
            session_id=session_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            metadata=metadata or {},
        )
        self._records.append(rec)
        if self._log_path:
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec.to_dict()) + "\n")
        return rec

    def total_tokens(self) -> int:
        return sum(r.total_tokens for r in self._records)

    def by_model(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for r in self._records:
            result[r.model] = result.get(r.model, 0) + r.total_tokens
        return result

    def by_session(self, session_id: str) -> list[TokenUsageRecord]:
        return [r for r in self._records if r.session_id == session_id]

    def session_total(self, session_id: str) -> int:
        return sum(r.total_tokens for r in self.by_session(session_id))

    def summary(self) -> dict:
        return {
            "total_records": len(self._records),
            "total_tokens": self.total_tokens(),
            "by_model": self.by_model(),
        }
