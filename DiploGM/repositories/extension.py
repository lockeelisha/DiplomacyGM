import datetime
from typing import Iterable, Optional

from DiploGM.db import database
from DiploGM.models.extension import ExtensionEvent
from DiploGM.repositories.base import BaseRepository


class ExtensionEventRepository(BaseRepository[ExtensionEvent]):
    def __init__(self) -> None:
        self.conn = database.get_connection()._connection
        self._initialise_schema()

    def _initialise_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extension_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                server_id INTEGER NOT NULL,
                hours REAL NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        self.conn.commit()

    def save(self, entity: ExtensionEvent) -> ExtensionEvent:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO extension_events (user_id, server_id, hours, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            (entity.user_id, entity.server_id, entity.hours, entity.reason, entity.created_at.isoformat()),
        )
        self.conn.commit()
        entity.id = cursor.lastrowid

        return entity

    def load(self, object_id: int) -> Optional[ExtensionEvent]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT (id, user_id, server_id, hours, reason, created_at) FROM extension_events WHERE id = ?;",
            (object_id,),
        )
        data = cursor.fetchone()
        if not data:
            return None

        entity = ExtensionEvent(
            id=data[0],
            user_id=data[1],
            server_id=data[2],
            hours=data[3],
            reason=data[4],
            created_at=datetime.datetime.fromisoformat(data[5])
        )

        return entity

    def delete(self, object_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM extension_events WHERE id = ?;",
            (object_id,),
        )
        self.conn.commit()

    def clear(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM extension_events;",
        )
        self.conn.commit()

    def all(self) -> Iterable[ExtensionEvent]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, server_id, hours, reason, created_at FROM extension_events;",
        )
        data = cursor.fetchall()
        if not data:
            return []

        return [
            ExtensionEvent(
            id=row[0],
            user_id=row[1],
            server_id=row[2],
            hours=row[3],
            reason=row[4],
            created_at=datetime.datetime.fromisoformat(row[5])
            ) for row in data
        ]

    def load_by_user(self, user_id: int) -> list[ExtensionEvent]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, server_id, hours, reason, created_at FROM extension_events WHERE user_id = ?;",
            (user_id,),
        )
        data = cursor.fetchall()
        if not data:
            return []

        return [
            ExtensionEvent(
            id=row[0],
            user_id=row[1],
            server_id=row[2],
            hours=row[3],
            reason=row[4],
            created_at=datetime.datetime.fromisoformat(row[5])
            ) for row in data
        ]

    def load_by_server(self, server_id: int) -> list[ExtensionEvent]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, user_id, server_id, hours, reason, created_at FROM extension_events WHERE server_id = ?;",
            (server_id,),
        )
        data = cursor.fetchall()
        if not data:
            return []

        return [
            ExtensionEvent(
            id=row[0],
            user_id=row[1],
            server_id=row[2],
            hours=row[3],
            reason=row[4],
            created_at=datetime.datetime.fromisoformat(row[5])
            ) for row in data
        ]

extension_repo = ExtensionEventRepository()
