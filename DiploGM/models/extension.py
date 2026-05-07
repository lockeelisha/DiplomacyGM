from __future__ import annotations
from dataclasses import dataclass, field
import datetime
import logging
from typing import Iterable, Optional

from DiploGM.db.database import get_connection
from DiploGM.utils.repository import Repository

logger = logging.getLogger(__name__)

@dataclass
class ExtensionEvent:
    user_id: int
    server_id: int
    hours: float
    id: Optional[int] = None
    reason: str = "unspecified"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self) -> dict:
        return {
            "user_id": self.user_id,
            "server_id": self.server_id,
            "hours": self.hours,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_json(cls, data: dict) -> ExtensionEvent:
        return ExtensionEvent(
            user_id=data["user_id"],
            server_id=data["server_id"],
            hours=data["hours"],
            reason=data["reason"],
            created_at=datetime.datetime.fromisoformat(data["created_at"])
        )

