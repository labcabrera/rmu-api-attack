from app.domain.entities.attack import Attack
from app.application.ports import AttackRepository


class SearchAttackByIdUseCase:
    """Use case for searching an attack by its ID"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(
        self,
        attack_id: str,
    ) -> Attack:
        return await self._attack_repository.find_by_id(attack_id)
