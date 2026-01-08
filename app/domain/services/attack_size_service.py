from app.domain.entities.attack import Attack


class AttackSizeService:
    """Domain service for attack business logic"""

    def get_critical_size_modifier(attack: Attack) -> None:
        return attack.modifiers.attack_size or 0

    def get_hit_size_multiplier(attack: Attack) -> float:
        check = attack.modifiers.attack_size or 0
        return 1.0 + (check * 1.5)
