"""
MongoDB converter for Attack entities.
This class handles conversion between Attack domain entities and MongoDB documents.
"""

from typing import Dict, Any, Optional
from bson import ObjectId
from app.domain.entities import (
    Attack,
    AttackResult,
)


class AttackToMongoConverter:
    """Converter for Attack entities to MongoDB documents"""

    @staticmethod
    def attack_to_dict(attack: Attack, include_id: bool = True) -> Dict[str, Any]:
        """Convert Attack domain entity to dictionary for MongoDB"""

        attack_dict = {
            "gameId": attack.game_id,
            "actionId": attack.action_id,
            "sourceId": attack.source_id,
            "targetId": attack.target_id,
            "status": attack.status.value,
            "modifiers": {
                "attackType": attack.modifiers.attack_type.value,
                "attackTable": attack.modifiers.attack_table,
                "attackSize": attack.modifiers.attack_size,
                "fumbleTable": attack.modifiers.fumble_table,
                "armor": {
                    "at": attack.modifiers.armor.at,
                    "body_at": attack.modifiers.armor.body_at,
                    "head_at": attack.modifiers.armor.head_at,
                    "arms_at": attack.modifiers.armor.arms_at,
                    "legs_at": attack.modifiers.armor.legs_at,
                },
                "actionPoints": attack.modifiers.action_points,
                "fumble": attack.modifiers.fumble,
                "calledShot": getattr(attack.modifiers, "called_shot", None),
                "rollModifiers": {
                    "bo": attack.modifiers.roll_modifiers.bo,
                    "bd": attack.modifiers.roll_modifiers.bd,
                    "injuryPenalty": attack.modifiers.roll_modifiers.injury_penalty,
                    "pacePenalty": attack.modifiers.roll_modifiers.pace_penalty,
                    "fatiguePenalty": attack.modifiers.roll_modifiers.fatigue_penalty,
                    "calledShotPenalty": attack.modifiers.roll_modifiers.called_shot_penalty,
                    "rangePenalty": attack.modifiers.roll_modifiers.range_penalty,
                    "shield": attack.modifiers.roll_modifiers.shield,
                    "parry": attack.modifiers.roll_modifiers.parry,
                    "attackNumber": attack.modifiers.roll_modifiers.attack_number,
                    "attackTargets": attack.modifiers.roll_modifiers.attack_targets,
                    "gameLethality": attack.modifiers.roll_modifiers.game_lethality,
                    "customBonus": attack.modifiers.roll_modifiers.custom_bonus,
                },
                "situationalModifiers": {
                    "cover": attack.modifiers.situational_modifiers.cover.value,
                    "restrictedQuarters": attack.modifiers.situational_modifiers.restricted_quarters.value,
                    "positionalSource": attack.modifiers.situational_modifiers.positional_source.value,
                    "positionalTarget": attack.modifiers.situational_modifiers.positional_target.value,
                    "dodge": attack.modifiers.situational_modifiers.dodge.value,
                    "disabledDb": attack.modifiers.situational_modifiers.disabled_db,
                    "disabledShield": attack.modifiers.situational_modifiers.disabled_shield,
                    "disabledParry": attack.modifiers.situational_modifiers.disabled_parry,
                    "sizeDifference": attack.modifiers.situational_modifiers.size_difference,
                    "offHand": attack.modifiers.situational_modifiers.off_hand,
                    "twoHandedWeapon": attack.modifiers.situational_modifiers.two_handed_weapon,
                    "higherGround": attack.modifiers.situational_modifiers.higher_ground,
                    "sourceStatus": attack.modifiers.situational_modifiers.source_status
                    or [],
                    "targetStatus": attack.modifiers.situational_modifiers.target_status
                    or [],
                },
                "features": [
                    {"key": feature.key, "value": feature.value}
                    for feature in attack.modifiers.features or []
                ],
                "sourceSkills": [
                    {"skillId": skill.skill_id, "bonus": skill.bonus}
                    for skill in attack.modifiers.source_skills or []
                ],
            },
        }

        # Only add _id if requested and attack has an id (for updates)
        if include_id and attack.id:
            attack_dict["_id"] = ObjectId(attack.id)

        # Handle roll conversion
        if attack.roll:
            attack_dict["roll"] = {
                "roll": attack.roll.roll,
                "location": attack.roll.location or None,
                "at": attack.roll.at or None,
                "criticalRolls": attack.roll.critical_rolls or None,
                "fumbleRoll": attack.roll.fumble_roll or None,
            }
        else:
            attack_dict["roll"] = None

        # Handle calculated conversion
        if attack.calculated:
            attack_dict["calculated"] = {
                "rollModifiers": [
                    {"key": modifier.key, "value": modifier.value}
                    for modifier in attack.calculated.roll_modifiers
                ],
                "criticalModifiers": [
                    {"key": modifier.key, "value": modifier.value}
                    for modifier in attack.calculated.critical_modifiers
                ],
                "criticalSeverityModifiers": [
                    {"key": modifier.key, "value": modifier.value}
                    for modifier in attack.calculated.critical_severity_modifiers
                ],
                "rollTotal": attack.calculated.roll_total,
                "criticalTotal": attack.calculated.critical_total,
                "criticalSeverityTotal": attack.calculated.critical_severity_total,
                "criticalSizeModifier": attack.calculated.critical_size_modifier,
                "hitSizeMultiplier": attack.calculated.hit_size_multiplier,
            }
        else:
            attack_dict["calculated"] = None

        # Handle results conversion
        if attack.results:
            attack_dict["results"] = AttackToMongoConverter.attack_result_to_dict(
                attack.results
            )
        else:
            attack_dict["results"] = None

        return attack_dict

    @staticmethod
    def attack_result_to_dict(attack_result: AttackResult) -> Dict[str, Any]:
        """Convert AttackResult domain entity to dictionary for MongoDB"""
        result_dict = {}
        if attack_result.attack_table_entry:
            result_dict["attackTableEntry"] = {
                "text": attack_result.attack_table_entry.text,
                "damage": attack_result.attack_table_entry.damage,
                "criticalType": attack_result.attack_table_entry.critical_type,
                "criticalSeverity": attack_result.attack_table_entry.critical_severity,
            }
        if attack_result.criticals:
            criticals = []
            for c in attack_result.criticals:
                critical_effects = None
                if c.result and c.result.effects:
                    critical_effects = []
                    for effect in c.result.effects:
                        critical_effects.append(
                            {
                                "status": effect.status,
                                "rounds": effect.rounds,
                                "value": effect.value,
                                "delay": effect.delay,
                                "condition": effect.condition,
                            }
                        )
                critical_result = (
                    {
                        "text": c.result.text,
                        "damage": c.result.damage,
                        "location": c.result.location,
                        "effects": critical_effects,
                    }
                    if c.result
                    else None
                )
                criticals.append(
                    {
                        "key": c.key,
                        "status": c.status.value,
                        "type": c.critical_type,
                        "criticalSeverity": c.critical_severity,
                        "adjustedRoll": c.adjusted_roll,
                        "result": critical_result,
                    }
                )
            result_dict["criticals"] = criticals

        if attack_result.fumble:
            result_dict["fumble"] = {
                "status": attack_result.fumble.status.value,
                "text": attack_result.fumble.text,
                "additionalDamageText": attack_result.fumble.additional_damage_text,
                "damage": attack_result.fumble.damage,
            }

        return result_dict
