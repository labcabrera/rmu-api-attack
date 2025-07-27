"""
MongoDB converter for Attack entities.
This class handles conversion between Attack domain entities and MongoDB documents.
"""

from typing import Dict, Any, Optional
from bson import ObjectId

from app.domain.entities import (
    Attack,
    AttackModifiers,
    AttackRoll,
    AttackResult,
    AttackRollModifiers,
    AttackCalculations,
    AttackBonusEntry,
    AttackSituationalModifiers,
    AttackTableEntry,
    AttackCriticalResult,
    AttackFeature,
    AttackSkill,
)
from app.domain.entities.enums import (
    AttackStatus,
    AttackType,
    Cover,
    PositionalSource,
    PositionalTarget,
    RestrictedQuarters,
    DodgeType,
)


class MongoAttackConverter:
    """Converter for Attack entities to/from MongoDB documents"""

    @staticmethod
    def attack_to_dict(attack: Attack, include_id: bool = True) -> Dict[str, Any]:
        """Convert Attack domain entity to dictionary for MongoDB"""

        attack_dict = {
            "actionId": attack.action_id,
            "sourceId": attack.source_id,
            "targetId": attack.target_id,
            "status": attack.status.value,
            "modifiers": {
                "attackType": attack.modifiers.attack_type.value,
                "attackTable": attack.modifiers.attack_table,
                "attackSize": attack.modifiers.attack_size,
                "at": attack.modifiers.at,
                "actionPoints": attack.modifiers.action_points,
                "rollModifiers": {
                    "bo": attack.modifiers.roll_modifiers.bo,
                    "boInjuryPenalty": attack.modifiers.roll_modifiers.bo_injury_penalty,
                    "boPacePenalty": attack.modifiers.roll_modifiers.bo_pace_penalty,
                    "boFatiguePenalty": attack.modifiers.roll_modifiers.bo_fatigue_penalty,
                    "bd": attack.modifiers.roll_modifiers.bd,
                    "rangePenalty": attack.modifiers.roll_modifiers.range_penalty,
                    "parry": attack.modifiers.roll_modifiers.parry,
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
                    "sizeDifference": attack.modifiers.situational_modifiers.size_difference,
                    "offHand": attack.modifiers.situational_modifiers.off_hand,
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
            attack_dict["roll"] = {"roll": attack.roll.roll}
        else:
            attack_dict["roll"] = None

        # Handle calculated conversion
        if attack.calculated:
            attack_dict["calculated"] = {
                "total": attack.calculated.total,
                "modifiers": [
                    {"key": modifier.key, "value": modifier.value}
                    for modifier in attack.calculated.modifiers
                ],
            }
        else:
            attack_dict["calculated"] = None

        # Handle results conversion
        if attack.results:
            results_dict = {}

            if attack.results.attack_table_entry:
                results_dict["attackTableEntry"] = {
                    "literal": attack.results.attack_table_entry.literal,
                    "damage": attack.results.attack_table_entry.damage,
                    "criticalType": attack.results.attack_table_entry.criticalType,
                    "criticalSeverity": attack.results.attack_table_entry.criticalSeverity,
                }

            attack_dict["results"] = results_dict
        else:
            attack_dict["results"] = None

        return attack_dict

    @staticmethod
    def dict_to_attack(attack_dict: Dict[str, Any]) -> Optional[Attack]:
        """Convert dictionary from MongoDB to Attack domain entity"""

        if not attack_dict:
            return None

        attack_id = str(attack_dict["_id"])
        modifiers_data = attack_dict.get("modifiers", {})

        roll_modifiers_data = modifiers_data.get("rollModifiers", {})
        roll_modifiers = AttackRollModifiers(
            bo=roll_modifiers_data.get("bo", 0),
            bo_injury_penalty=roll_modifiers_data.get("boInjuryPenalty", 0),
            bo_pace_penalty=roll_modifiers_data.get("boPacePenalty", 0),
            bo_fatigue_penalty=roll_modifiers_data.get("boFatiguePenalty", 0),
            bd=roll_modifiers_data.get("bd", 0),
            range_penalty=roll_modifiers_data.get("rangePenalty", 0),
            parry=roll_modifiers_data.get("parry", 0),
            custom_bonus=roll_modifiers_data.get("customBonus", 0),
        )

        situational_modifiers_data = modifiers_data.get("situationalModifiers", {})
        situational_modifiers = AttackSituationalModifiers(
            cover=Cover.from_value(situational_modifiers_data.get("cover", "none")),
            restricted_quarters=RestrictedQuarters.from_value(
                situational_modifiers_data.get("restrictedQuarters", "none")
            ),
            positional_source=PositionalSource.from_value(
                situational_modifiers_data.get("positionalSource", "none")
            ),
            positional_target=PositionalTarget.from_value(
                situational_modifiers_data.get("positionalTarget", "none")
            ),
            dodge=DodgeType.from_value(situational_modifiers_data.get("dodge", "none")),
            disabled_db=situational_modifiers_data.get("disabledDb", False),
            disabled_shield=situational_modifiers_data.get("disabledShield", False),
            size_difference=situational_modifiers_data.get("sizeDifference", 0),
            off_hand=situational_modifiers_data.get("offHand", False),
            higher_ground=situational_modifiers_data.get("higherGround", False),
            source_status=situational_modifiers_data.get("sourceStatus", []),
            target_status=situational_modifiers_data.get("targetStatus", []),
        )

        modifiers = AttackModifiers(
            attack_type=AttackType.from_value(modifiers_data["attackType"]),
            attack_table=attack_dict.get("modifiers", {}).get("attackTable", ""),
            attack_size=attack_dict.get("modifiers", {}).get("attackSize", ""),
            at=attack_dict.get("modifiers", {}).get("at", 0),
            action_points=attack_dict.get("modifiers", {}).get("actionPoints", 4),
            roll_modifiers=roll_modifiers,
            situational_modifiers=situational_modifiers,
            features=[
                AttackFeature(key=feature["key"], value=feature["value"])
                for feature in modifiers_data.get("features", [])
            ],
            source_skills=[
                AttackSkill(skill_id=skill["skillId"], bonus=skill["bonus"])
                for skill in modifiers_data.get("sourceSkills", [])
            ],
        )

        roll = None
        if attack_dict.get("roll"):
            roll = AttackRoll(roll=attack_dict["roll"]["roll"])

        # Handle calculated conversion
        calculated = None
        if attack_dict.get("calculated"):
            calculated_data = attack_dict["calculated"]
            modifiers_list = []
            for modifier_data in calculated_data.get("modifiers", []):
                modifier = AttackBonusEntry(
                    key=modifier_data["key"], value=modifier_data["value"]
                )
                modifiers_list.append(modifier)

            calculated = AttackCalculations(
                total=calculated_data.get("total", 0), modifiers=modifiers_list
            )

        results = None
        if attack_dict.get("results"):
            results_data = attack_dict["results"]
            criticals = []
            for c_data in results_data.get("criticals", []):
                critical = AttackCriticalResult(
                    id=c_data["id"],
                    type=c_data.get("type", "unknown"),
                    roll=c_data.get("roll", 0),
                    result=c_data.get("result", ""),
                    status=c_data["status"],
                )
                criticals.append(critical)

            # Handle attack table entry conversion
            attack_table_entry = None
            if results_data.get("attackTableEntry"):
                entry_data = results_data["attackTableEntry"]
                attack_table_entry = AttackTableEntry(
                    literal=entry_data["literal"],
                    damage=entry_data["damage"],
                    criticalType=entry_data.get("criticalType"),
                    criticalSeverity=entry_data.get("criticalSeverity"),
                )

            results = AttackResult()
            results.attack_table_entry = attack_table_entry

        if not "status" in attack_dict:
            raise ValueError("Attack dictionary must contain 'status' field")

        try:
            status = AttackStatus(attack_dict["status"])
        except ValueError:
            raise ValueError(f"Invalid 'status' value: {attack_dict['status']}")

        return Attack(
            id=attack_id,
            action_id=attack_dict.get("actionId", ""),
            source_id=attack_dict.get("sourceId", ""),
            target_id=attack_dict.get("targetId", ""),
            status=status,
            modifiers=modifiers,
            roll=roll,
            calculated=calculated,
            results=results,
        )
