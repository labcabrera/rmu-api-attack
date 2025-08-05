from app.application.ports.attack_ports import AttackRepository


class DeleteAttackUseCase:
    """Use case for deleting an attack"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(self, attack_id: str) -> bool:
        """Execute the delete attack use case"""
        return await self._attack_repository.delete(attack_id)
