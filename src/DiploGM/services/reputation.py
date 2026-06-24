from typing import Iterable

from DiploGM.models.rep_delta import ReputationDelta
from DiploGM.repositories import reputation_repo
from DiploGM.services.base import BaseService


class ReputationService(BaseService):
	def __init__(self) -> None:
		self.repo = reputation_repo

	def create_delta(
		self, user_id: int, delta: int, reason: str = "Unspecified"
	) -> ReputationDelta:
		entity = ReputationDelta(user_id, delta, reason)

		current_rep = self.get_user_value(user_id)
		if current_rep > 10:
			entity.delta = -(current_rep - 10)
			entity.reason += " (adjusted to match cap reputation of 10)"
		elif current_rep + delta >= 10:
			entity.delta = (current_rep + delta) - 10
			entity.reason += " (truncated gains to cap repuation at 10)"

		self.repo.save(entity)
		return entity

	def delete_delta(self, delta_id: int) -> bool:
		entity = self.repo.load(delta_id)
		if entity is None:
			return False

		self.repo.delete(delta_id)
		return True

	def _initialise_user_reputation(self, user_id: int) -> ReputationDelta:
		initial = ReputationDelta(user_id, 10, "Initial Reputation")
		return self.repo.save(initial)

	def get_user_history(self, user_id: int) -> Iterable[ReputationDelta]:
		history = []

		history.extend(self.repo.find_by(lambda d: d.user_id == user_id))
		if len(history) == 0:
			entity = self._initialise_user_reputation(user_id)
			history.append(entity)

		return history

	def get_user_value(self, user_id: int) -> int:
		history = []

		history.extend(self.repo.find_by(lambda d: d.user_id == user_id))
		if len(history) == 0:
			entity = self._initialise_user_reputation(user_id)
			history.append(entity)

		values = map(lambda d: d.delta, history)
		return sum(values)


reputation_service = ReputationService()
