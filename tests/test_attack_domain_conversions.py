from app.domain.entities import (
    Attack,
    AttackArmor,
    AttackModifiers,
    AttackRoll,
    AttackRollModifiers,
    AttackSituationalModifiers,
)
from app.domain.entities.enums import AttackStatus, AttackType
from app.interfaces.http.dto import AttackDTO, CreateAttackRequestDTO


def build_attack_modifiers() -> AttackModifiers:
    return AttackModifiers(
        attack_type=AttackType.MELEE,
        attack_table="arming-sword",
        attack_size=2,
        fumble_table="melee-one-hand",
        armor=AttackArmor(at=1),
        action_points=4,
        fumble=2,
        roll_modifiers=AttackRollModifiers(bo=85, bd=25, parry=10),
        situational_modifiers=AttackSituationalModifiers(
            source_status=[],
            target_status=[],
        ),
        features=[],
        source_skills=[],
    )


def test_attack_entity_to_dto_conversion():
    attack = Attack(
        id="attack_001",
        game_id="game_001",
        action_id="action_001",
        source_id="source_001",
        target_id="target_001",
        status=AttackStatus.APPLIED,
        modifiers=build_attack_modifiers(),
        roll=AttackRoll(roll=91, at=1),
    )

    attack_dto = AttackDTO.from_entity(attack)

    assert attack_dto.id == "attack_001"
    assert attack_dto.gameId == "game_001"
    assert attack_dto.actionId == "action_001"
    assert attack_dto.status == AttackStatus.APPLIED.value
    assert attack_dto.modifiers.attackTable == "arming-sword"
    assert attack_dto.modifiers.rollModifiers.bo == 85
    assert attack_dto.roll.roll == 91


def test_create_attack_request_to_command_conversion():
    request = CreateAttackRequestDTO(
        gameId="game_001",
        actionId="action_001",
        sourceId="source_001",
        targetId="target_001",
        modifiers=AttackDTO.from_entity(
            Attack(
                id="attack_001",
                game_id="game_001",
                action_id="action_001",
                source_id="source_001",
                target_id="target_001",
                status=AttackStatus.PENDING_ATTACK_ROLL,
                modifiers=build_attack_modifiers(),
            )
        ).modifiers,
    )

    command = request.to_command()

    assert command.game_id == "game_001"
    assert command.action_id == "action_001"
    assert command.source_id == "source_001"
    assert command.target_id == "target_001"
    assert command.modifiers.attack_type == AttackType.MELEE
    assert command.modifiers.armor.at == 1
