from app.domain.entities.attack import Attack


class AttackSizeService:
    """Domain service for attack business logic"""

    def get_critical_size_modifier(attack: Attack) -> None:
        """Return an integer modifier for critical calculations based on attack size."""
        return attack.modifiers.attack_size or 0

    def get_hit_size_multiplier(attack: Attack) -> float:
        """Return a float multiplier applied to hit calculations based on size."""
        tmp = attack.modifiers.attack_size or 0
        return 1.0 + (float(tmp) * 0.5)
