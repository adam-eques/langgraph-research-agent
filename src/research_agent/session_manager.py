from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Session:
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)
    context: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)

    def update_context(self, key: str, value) -> None:
        self.context[key] = value
        self.last_active = time.time()

    def add_turn(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content, "ts": time.time()})
        self.last_active = time.time()

    def age_seconds(self) -> float:
        return time.time() - self.created_at

    def is_expired(self, ttl: float = 3600.0) -> bool:
        return time.time() - self.last_active > ttl


class SessionManager:
    def __init__(self, storage_dir: str = ".sessions", ttl: float = 3600.0) -> None:
        self._dir = Path(storage_dir)
        self._dir.mkdir(exist_ok=True)
        self._ttl = ttl
        self._sessions: dict[str, Session] = {}

    def create(self, context: dict | None = None) -> Session:
        sid = hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16]
        session = Session(session_id=sid, context=context or {})
        self._sessions[sid] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def expire(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def cleanup_expired(self) -> int:
        expired = [sid for sid, s in self._sessions.items() if s.is_expired(self._ttl)]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    @property
    def active_count(self) -> int:
        return len(self._sessions)
