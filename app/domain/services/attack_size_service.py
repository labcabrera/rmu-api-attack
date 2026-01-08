from app.domain.entities.attack import Attack


class AttackSizeService:
    """Domain service for attack business logic"""

    @staticmethod
    def get_critical_size_modifier(attack: Attack) -> int:
        """Return an integer modifier for critical calculations based on attack size."""
        if not attack or not getattr(attack, "modifiers", None):
            return 0
        return int(getattr(attack.modifiers, "attack_size", 0) or 0)

    @staticmethod
    def get_hit_size_multiplier(attack: Attack) -> float:
        """Return a float multiplier applied to hit calculations based on size."""
        if not attack or not getattr(attack, "modifiers", None):
            return 1.0
        tmp = getattr(attack.modifiers, "attack_size", 0) or 0
        try:
            return 1.0 + (float(tmp) * 0.5)
        except Exception:
            return 1.0

    @staticmethod
    def get_adjusted_severity(severity: str, sizeModifier: int) -> str:
        """Return adjusted critical severity based on attack size.

        Maps severities A..E to indices 0..4, adds `sizeModifier`, clamps to range
        and returns the corresponding severity letter. If `severity` is falsy or
        not in the map, it is returned unchanged.
        Example: severity='A', sizeModifier=1 -> 'B'
        """
        if not severity:
            return severity

        severity_map = ["Z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        try:
            idx = severity_map.index(severity)
        except ValueError:
            # Unknown severity, return as-is
            return severity

        try:
            new_idx = idx + int(sizeModifier)
        except Exception:
            new_idx = idx

        # Clamp
        new_idx = max(0, min(new_idx, len(severity_map) - 1))
        return severity_map[new_idx]
