from dataclasses import dataclass


@dataclass
class AttackFeature:
    """Attack feature data"""

    key: str = None
    value: str = None
