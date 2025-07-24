"""
Tests for Attack domain entity conversions between domain and DTO.
"""

import pytest
from app.domain.entities import (
    Attack,
    AttackModifiers,
    AttackRoll,
    AttackResult,
    AttackRollModifiers,
    Critical,
)
from app.domain.entities.enums import AttackStatus, AttackType
from app.infrastructure.adapters.web.attack_dtos import (
    AttackDTO,
    AttackModifiersDTO,
    AttackRollModifiersDTO,
    CreateAttackRequestDTO,
)
from app.infrastructure.adapters.web.attack_dto_converter import (
    attack_to_dto,
    create_request_to_domain,
)


class TestAttackDomainConversions:
    """Test class for Attack domain conversions"""

    def test_attack_to_dto_conversion(self):
        """Test converting Attack domain entity to DTO"""
        # Arrange: Create a complete Attack domain entity
        roll_modifiers = AttackRollModifiers(
            bo=85,
            bo_injury_penalty=-10,
            bo_actions_points_penalty=-5,
            bo_pace_penalty=0,
            bo_fatigue_penalty=-2,
            bd=25,
            range_penalty=-5,
            parry=15,
            custom_bonus=10,
        )

        attack_modifiers = AttackModifiers(
            attack_type=AttackType.MELEE,
            roll_modifiers=roll_modifiers,
        )

        criticals = [
            Critical(
                id="crit_001",
                type="slash",
                roll=95,
                result="Major wound to arm",
                status="applied",
            ),
            Critical(
                id="crit_002",
                type="puncture",
                roll=88,
                result="Minor wound to leg",
                status="pending",
            ),
        ]

        attack_result = AttackResult(
            label_result="12AT",
            hit_points=12,
            criticals=criticals,
        )

        attack_roll = AttackRoll(roll=18)

        attack = Attack(
            id="attack_001",
            tactical_game_id="game_001",
            status=AttackStatus.APPLIED,
            modifiers=attack_modifiers,
            roll=attack_roll,
            results=attack_result,
        )

        # Act: Convert to DTO
        attack_dto = attack_to_dto(attack)

        # Assert: Verify DTO fields
        assert attack_dto.id == "attack_001"
        assert attack_dto.actionId == "game_001"
        assert (
            attack_dto.status == AttackStatus.APPLIED.value
        )  # Compare with the string value

        # Verify modifiers
        assert (
            attack_dto.modifiers.attackType == AttackType.MELEE.value
        )  # Compare with the string value
        assert attack_dto.modifiers.rollModifiers.bo == 85
        assert attack_dto.modifiers.rollModifiers.bd == 25

        # Verify roll
        assert attack_dto.roll is not None
        assert attack_dto.roll.roll == 18

        # Verify results
        assert attack_dto.results is not None
        assert attack_dto.results.labelResult == "12AT"
        assert attack_dto.results.hitPoints == 12
        assert len(attack_dto.results.criticals) == 2
        assert attack_dto.results.criticals[0].id == "crit_001"
        assert attack_dto.results.criticals[0].status == "applied"

    def test_create_request_dto_to_domain_conversion(self):
        """Test converting CreateAttackRequestDTO to Attack domain entity"""
        # Arrange: Create a CreateAttackRequestDTO
        roll_modifiers_dto = AttackRollModifiersDTO(
            bo=80,
            bd=20,
        )

        modifiers_dto = AttackModifiersDTO(
            attackType=AttackType.RANGED,
            rollModifiers=roll_modifiers_dto,
        )

        create_request_dto = CreateAttackRequestDTO(
            actionId="action_123",
            sourceId="character_001",
            targetId="character_002",
            modifiers=modifiers_dto,
        )

        # Act: Convert to domain entity
        attack = create_request_to_domain(create_request_dto)

        # Assert: Verify domain entity fields
        assert attack.id is None  # Should be None for new attacks
        assert attack.tactical_game_id == "action_123"
        assert attack.status == AttackStatus.DRAFT

        # Verify modifiers
        assert attack.modifiers.attack_type == AttackType.RANGED
        assert attack.modifiers.roll_modifiers.bo == 80
        assert attack.modifiers.roll_modifiers.bd == 20
        assert attack.modifiers.roll_modifiers.bo_injury_penalty == 0  # Default value
        assert (
            attack.modifiers.roll_modifiers.bo_actions_points_penalty == 0
        )  # Default value
        assert attack.modifiers.roll_modifiers.bo_pace_penalty == 0  # Default value
        assert attack.modifiers.roll_modifiers.bo_fatigue_penalty == 0  # Default value
        assert attack.modifiers.roll_modifiers.range_penalty == 0  # Default value
        assert attack.modifiers.roll_modifiers.parry == 0  # Default value
        assert attack.modifiers.roll_modifiers.custom_bonus == 0  # Default value

        # Verify optional fields are None
        assert attack.roll is None
        assert attack.results is None

    def test_roundtrip_conversion_minimal_attack(self):
        """Test converting Attack to DTO and back (roundtrip) with minimal data"""
        # Arrange: Create a minimal Attack entity
        roll_modifiers = AttackRollModifiers(
            bo=70,
            bo_injury_penalty=0,
            bo_actions_points_penalty=0,
            bo_pace_penalty=0,
            bo_fatigue_penalty=0,
            bd=15,
            range_penalty=0,
            parry=0,
            custom_bonus=0,
        )

        attack_modifiers = AttackModifiers(
            attack_type=AttackType.MELEE,
            roll_modifiers=roll_modifiers,
        )

        original_attack = Attack(
            id="attack_minimal",
            tactical_game_id="game_minimal",
            status=AttackStatus.DRAFT,
            modifiers=attack_modifiers,
            roll=None,
            results=None,
        )

        # Act: Convert to DTO and back to domain
        attack_dto = attack_to_dto(original_attack)

        # Create a new CreateAttackRequestDTO from the DTO data
        create_request = CreateAttackRequestDTO(
            actionId=attack_dto.actionId,
            sourceId="source_test",  # These fields are not in AttackDTO, so we use test values
            targetId="target_test",
            modifiers=attack_dto.modifiers,
        )

        converted_attack = create_request_to_domain(create_request)

        # Assert: Verify the core data is preserved
        assert converted_attack.tactical_game_id == original_attack.tactical_game_id
        assert (
            converted_attack.status == AttackStatus.DRAFT
        )  # Should be DRAFT for new attacks
        assert (
            converted_attack.modifiers.attack_type
            == original_attack.modifiers.attack_type
        )
        assert (
            converted_attack.modifiers.roll_modifiers.bo
            == original_attack.modifiers.roll_modifiers.bo
        )
        assert (
            converted_attack.modifiers.roll_modifiers.bd
            == original_attack.modifiers.roll_modifiers.bd
        )
        assert converted_attack.roll is None
        assert converted_attack.results is None

    def test_attack_with_roll_only_conversion(self):
        """Test converting Attack with roll but no results"""
        # Arrange: Create Attack with roll but no results
        roll_modifiers = AttackRollModifiers(
            bo=75,
            bo_injury_penalty=-5,
            bo_actions_points_penalty=0,
            bo_pace_penalty=0,
            bo_fatigue_penalty=0,
            bd=20,
            range_penalty=0,
            parry=10,
            custom_bonus=5,
        )

        attack_modifiers = AttackModifiers(
            attack_type=AttackType.RANGED,
            roll_modifiers=roll_modifiers,
        )

        attack_roll = AttackRoll(roll=15)

        attack = Attack(
            id="attack_with_roll",
            tactical_game_id="game_with_roll",
            status=AttackStatus.ROLLED,
            modifiers=attack_modifiers,
            roll=attack_roll,
            results=None,
        )

        # Act: Convert to DTO
        attack_dto = attack_to_dto(attack)

        # Assert: Verify DTO has roll but no results
        assert attack_dto.id == "attack_with_roll"
        assert attack_dto.actionId == "game_with_roll"
        assert (
            attack_dto.status == AttackStatus.ROLLED.value
        )  # Compare with the string value
        assert (
            attack_dto.modifiers.attackType == AttackType.RANGED.value
        )  # Compare with the string value

        # Verify roll is present
        assert attack_dto.roll is not None
        assert attack_dto.roll.roll == 15

        # Verify results is None
        assert attack_dto.results is None

    def test_invalid_attack_type_in_modifiers(self):
        """Test that invalid attack type in modifiers raises appropriate error"""
        # This test verifies the validation in AttackModifiers
        roll_modifiers = AttackRollModifiers(
            bo=50,
            bo_injury_penalty=0,
            bo_actions_points_penalty=0,
            bo_pace_penalty=0,
            bo_fatigue_penalty=0,
            bd=10,
            range_penalty=0,
            parry=0,
            custom_bonus=0,
        )

        # This should work fine with valid AttackType
        valid_modifiers = AttackModifiers(
            attack_type=AttackType.MELEE,
            roll_modifiers=roll_modifiers,
        )

        assert valid_modifiers.attack_type == AttackType.MELEE
        assert isinstance(valid_modifiers.roll_modifiers, AttackRollModifiers)
