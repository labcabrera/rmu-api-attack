import pytest

from app.domain.entities import (
    Attack,
    AttackModifiers,
    AttackRoll,
    AttackResult,
    AttackRollModifiers,
    AttackTableEntry,
    AttackSituationalModifiers,
)
from app.domain.entities.enums import (
    AttackStatus,
    AttackType,
    Cover,
    DodgeType,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
)
from app.infrastructure.adapters.web.attack_dto_converter import AttackDTOConverter


class TestAttackDTOConversions:

    def test_attack_dto_conversion(self):

        attack = Attack(
            id="attack_001",
            action_id="action_001",
            source_id="source_001",
            target_id="target_001",
            status=AttackStatus.DRAFT,
            modifiers=AttackModifiers(
                attack_type=AttackType.MELEE,
                attack_table="sword",
                attack_size="medium",
                at=5,
                roll_modifiers=AttackRollModifiers(
                    bo=85,
                    bo_injury_penalty=-10,
                    bo_actions_points_penalty=-5,
                    bo_pace_penalty=0,
                    bo_fatigue_penalty=-2,
                    bd=25,
                    range_penalty=-5,
                    parry=15,
                    custom_bonus=10,
                ),
                situational_modifiers=AttackSituationalModifiers(
                    cover=Cover.NONE,
                    restricted_quarters=RestrictedQuarters.NONE,
                    positional_source=PositionalSource.NONE,
                    positional_target=PositionalTarget.NONE,
                    dodge=DodgeType.NONE,
                    stunned_target=False,
                    disabled_db=False,
                    disabled_shield=False,
                    surprised=False,
                    prone_attacker=False,
                    prone_defender=False,
                    size_difference=0,
                    off_hand=False,
                    higher_ground=False,
                    range=0,
                    ranged_attack_in_melee=False,
                ),
            ),
            roll=AttackRoll(roll=90),
            results=AttackResult(
                label_result="Hit",
                hit_points=15,
                criticals=[],
                attack_table_entry=AttackTableEntry(
                    roll=85,
                    at=50,
                    literal="15 hits",
                    damage=15,
                    criticalType="Slash",
                    criticalSeverity="A",
                ),
            ),
        )

        # Convert to DTO
        attack_dto = AttackDTOConverter.attack_to_dto(attack)

        # Verify conversion
        assert attack_dto.id == "attack_001"
        assert attack_dto.actionId == "action_001"
        assert attack_dto.sourceId == "source_001"
        assert attack_dto.targetId == "target_001"

        # Verify new fields in modifiers
        assert attack_dto.modifiers.attackTable == "Slash"
        assert attack_dto.modifiers.attackSize == "M"
        assert attack_dto.modifiers.at == 50

        # Verify attack_table_entry in results
        assert attack_dto.results is not None
        assert attack_dto.results.attackTableEntry is not None
        assert attack_dto.results.attackTableEntry.roll == 85
        assert attack_dto.results.attackTableEntry.at == 50
        assert attack_dto.results.attackTableEntry.literal == "15 hits"
        assert attack_dto.results.attackTableEntry.damage == 15
        assert attack_dto.results.attackTableEntry.criticalType == "Slash"
        assert attack_dto.results.attackTableEntry.criticalSeverity == "A"


if __name__ == "__main__":
    pytest.main([__file__])
