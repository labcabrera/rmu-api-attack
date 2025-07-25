from typing import Any, Dict, Optional
from app.domain.entities.attack import Attack
from app.domain.entities.critical import Critical
from app.domain.ports.attack_ports import AttackNotificationPort, AttackRepository


class UpdateAttackModifiersUseCase:
    """Use case for updating an attack"""

    def __init__(
        self,
        attack_repository: AttackRepository,
        notification_port: Optional[AttackNotificationPort] = None,
    ):
        self._attack_repository = attack_repository
        self._notification_port = notification_port

    async def execute(
        self, attack_id: str, update_data: Dict[str, Any]
    ) -> Optional[Attack]:
        """Execute the update attack use case"""
        attack = await self._attack_repository.find_by_id(attack_id)
        if not attack:
            return None

        # Apply updates to the attack
        if "status" in update_data:
            attack.status = update_data["status"]

        if "roll" in update_data and update_data["roll"]:
            attack.execute_roll(update_data["roll"]["roll"])

        if "results" in update_data and update_data["results"]:
            results_data = update_data["results"]
            criticals = []
            if "criticals" in results_data:
                criticals = [
                    Critical(id=c.get("id", ""), status=c.get("status", ""))
                    for c in results_data["criticals"]
                ]
            attack.apply_results(
                results_data.get("label_result", ""),
                results_data.get("hit_points", 0),
                criticals,
            )

        updated_attack = await self._attack_repository.update(attack)

        if self._notification_port and updated_attack:
            await self._notification_port.notify_attack_updated(updated_attack)

        return updated_attack
