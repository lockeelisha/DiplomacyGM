from DiploGM.models.extension import ExtensionEvent
from DiploGM.repositories.extension_repo import extension_repo
from DiploGM.services.base import BaseService

class ExtensionService(BaseService):
    def __init__(self) -> None:
        self.count = max(e.id for e in extension_repo.all() if e.id)

    def record_extension(self, user_id: int, game_id: int, hours: float = 1.0, reason: str = "Unspecified") -> int | None:
        event = ExtensionEvent(
            user_id=user_id,
            server_id=game_id,
            hours=hours,
            reason=reason
        )

        try:
            extension_repo.save(event)
        except Exception:
            return None
        else:
            self.count += 1

        return self.count

    def delete_extension(self, grace_id: int) -> None:
        extension_repo.delete(grace_id)

    def view_user_extensions(self, user_id: int) -> dict:
        events = extension_repo.load_by_user(user_id)

        servers = {}
        for e in sorted(events, key=lambda e: (e.server_id, e.created_at), reverse=True):
            servers[e.server_id] = servers.get(e.server_id, set()).add(e)

        return servers

    def view_server_extensions(self, server_id: int) -> dict[int, set[ExtensionEvent]]:
        events = extension_repo.load_by_server(server_id)

        users = {}
        for e in sorted(events, key=lambda e: (e.user_id, e.created_at), reverse=True):
            users[e.server_id] = users.get(e.server_id, set()).add(e)

        return users

extension_service = ExtensionService()
