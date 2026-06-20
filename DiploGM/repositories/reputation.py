import datetime
from typing import Optional, Iterable

from DiploGM.db.database import get_connection
from DiploGM.models.rep_delta import ReputationDelta
from DiploGM.repositories.base import BaseRepository


class ReputationDeltaRepository(BaseRepository[ReputationDelta]):
    def __init__(self) -> None:
        self.conn = get_connection()._connection
        self._initialise_schema()

    def _initialise_schema(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reputation_deltas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                delta INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save(self, entity: ReputationDelta) -> ReputationDelta:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO reputation_deltas (user_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
            (
                entity.user_id,
                entity.delta,
                entity.reason,
                entity.created_at.isoformat(),
            ),
        )

        entity.id = cursor.lastrowid
        return entity

    def load(self, object_id: int) -> Optional[ReputationDelta]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT (id, user_id, delta, reason, created_at) FROM reputation_deltas WHERE id = ?", (id,))
        row = cursor.fetchone()
        if not row:
            return None

        return ReputationDelta(
            id=row[0],
            user_id=row[1],
            delta=row[2],
            reason=row[3],
            created_at=datetime.datetime.fromisoformat(row[4])
        )

    def delete(self, object_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM reputation_deltas WHERE id = ?", (object_id,))
        self.conn.commit()

    def clear(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM reputation_deltas")
        self.conn.commit()

    def all(self) -> Iterable[ReputationDelta]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reputation_deltas")
        rows = cursor.fetchall()

        data = [
            ReputationDelta(
                id=row[0],
                user_id=row[1],
                delta=row[2],
                reason=row[3],
                created_at=datetime.datetime.fromisoformat(row[4])
            ) for row in rows
        ]

        return data

reputation_repo = ReputationDeltaRepository()
