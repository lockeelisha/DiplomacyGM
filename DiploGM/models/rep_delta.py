from __future__ import annotations
from dataclasses import dataclass, field
import datetime
from typing import Optional


@dataclass
class ReputationDelta:
    user_id: int
    delta: int
    reason: str = "unspecified"
    id: Optional[int] = None
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "delta": self.delta,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
        }

    @staticmethod
    def from_json(data: dict) -> ReputationDelta:
        return ReputationDelta(
            id=int(data["id"]),
            user_id=int(data["user_id"]),
            delta=int(data["delta"]),
            reason=data["reason"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]),
        )
