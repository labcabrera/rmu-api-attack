from app.domain.entities import (
    AttackArmor,
    AttackModifiers,
    AttackRollModifiers,
    AttackSituationalModifiers,
)
from app.domain.entities.enums import AttackType, Cover
from app.interfaces.http.dto import AttackModifiersDTO


def test_attack_modifiers_dto_roundtrip():
    modifiers = AttackModifiers(
        attack_type=AttackType.RANGED,
        attack_table="long-bow",
        attack_size=2,
        fumble_table="missile",
        armor=AttackArmor(at=4),
        action_points=3,
        fumble=3,
        roll_modifiers=AttackRollModifiers(
            bo=90,
            bd=15,
            range_penalty=-20,
            custom_bonus=5,
        ),
        situational_modifiers=AttackSituationalModifiers(
            cover=Cover.SOFT_PARTIAL,
            source_status=["focused"],
            target_status=["prone"],
        ),
        features=[],
        source_skills=[],
    )

    dto = AttackModifiersDTO.from_entity(modifiers)
    converted = dto.to_entity()

    assert dto.attackType == AttackType.RANGED.value
    assert dto.attackTable == "long-bow"
    assert dto.armor.at == 4
    assert dto.rollModifiers.rangePenalty == -20
    assert converted.attack_type == AttackType.RANGED
    assert converted.attack_table == "long-bow"
    assert converted.armor.at == 4
    assert converted.roll_modifiers.custom_bonus == 5
    assert converted.situational_modifiers.cover == Cover.SOFT_PARTIAL
