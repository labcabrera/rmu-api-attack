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
    AttackFeature,
    AttackSkill,
    AttackCriticalResult,
)
from app.domain.entities.enums import (
    AttackStatus,
    AttackType,
    Cover,
    CriticalStatus,
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
                "fumble": attack.modifiers.fumble,
                "rollModifiers": {
                    "bo": attack.modifiers.roll_modifiers.bo,
                    "bd": attack.modifiers.roll_modifiers.bd,
                    "injuryPenalty": attack.modifiers.roll_modifiers.injury_penalty,
                    "pacePenalty": attack.modifiers.roll_modifiers.pace_penalty,
                    "fatiguePenalty": attack.modifiers.roll_modifiers.fatigue_penalty,
                    "rangePenalty": attack.modifiers.roll_modifiers.range_penalty,
                    "shield": attack.modifiers.roll_modifiers.shield,
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
            attack_dict["roll"] = {"roll": attack.roll.roll}
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
            }
        else:
            attack_dict["calculated"] = None

        # Handle results conversion
        if attack.results:
            attack_dict["results"] = MongoAttackConverter.attack_result_to_dict(
                attack.results
            )
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
            bd=roll_modifiers_data.get("bd", 0),
            injury_penalty=roll_modifiers_data.get("injuryPenalty", 0),
            pace_penalty=roll_modifiers_data.get("pacePenalty", 0),
            fatigue_penalty=roll_modifiers_data.get("fatiguePenalty", 0),
            range_penalty=roll_modifiers_data.get("rangePenalty", 0),
            shield=roll_modifiers_data.get("shield", 0),
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
            disabled_parry=situational_modifiers_data.get("disabledParry", False),
            size_difference=situational_modifiers_data.get("sizeDifference", 0),
            off_hand=situational_modifiers_data.get("offHand", False),
            two_handed_weapon=situational_modifiers_data.get("twoHandedWeapon", False),
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
            fumble=attack_dict.get("modifiers", {}).get("fumble", 1),
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
            for modifier_data in calculated_data.get("rollModifiers", []):
                modifier = AttackBonusEntry(
                    key=modifier_data["key"], value=modifier_data["value"]
                )
                modifiers_list.append(modifier)

            critical_modifiers_list = []
            for critical_modifier_data in calculated_data.get("criticalModifiers", []):
                critical_modifier = AttackBonusEntry(
                    key=critical_modifier_data["key"],
                    value=critical_modifier_data["value"],
                )
                critical_modifiers_list.append(critical_modifier)

            critical_severity_modifiers_list = []
            for critical_severity_modifier_data in calculated_data.get(
                "criticalSeverityModifiers", []
            ):
                critical_modifier = AttackBonusEntry(
                    key=critical_severity_modifier_data["key"],
                    value=critical_severity_modifier_data["value"],
                )
                critical_severity_modifiers_list.append(critical_modifier)

            calculated = AttackCalculations(
                roll_modifiers=modifiers_list,
                critical_modifiers=critical_modifiers_list,
                critical_severity_modifiers=critical_severity_modifiers_list,
                roll_total=calculated_data.get("rollTotal", 0),
                critical_total=calculated_data.get("criticalTotal", 0),
                critical_severity_total=calculated_data.get("criticalSeverityTotal", 0),
            )

        results = None
        if attack_dict.get("results"):
            attack_table_entry = None
            results_data = attack_dict["results"]
            if results_data.get("attackTableEntry"):
                entry_data = results_data["attackTableEntry"]
                attack_table_entry = AttackTableEntry(
                    text=entry_data["text"],
                    damage=entry_data["damage"],
                    critical_type=entry_data.get("criticalType"),
                    critical_severity=entry_data.get("criticalSeverity"),
                )

            criticals = []
            for c_data in results_data.get("criticals", []):
                critical = AttackCriticalResult(
                    key=c_data["key"],
                    status=CriticalStatus.from_value(c_data["status"]),
                    critical_type=c_data.get("type", "unknown"),
                    critical_severity=c_data.get("criticalSeverity", None),
                    adjusted_roll=c_data.get("adjustedRoll", 0),
                    # result=c_data.get("result", ""),
                )
                criticals.append(critical)
            results = AttackResult(
                attack_table_entry=attack_table_entry,
                criticals=criticals,
            )

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
            result_dict["criticals"] = [
                {
                    "key": critical.key,
                    "status": critical.status.value,
                    "type": critical.critical_type,
                    "criticalSeverity": critical.critical_severity,
                    "adjustedRoll": critical.adjusted_roll,
                    "result": (
                        {
                            "text": (
                                critical.result.text
                                if hasattr(critical, "result")
                                else None
                            ),
                        }
                        if critical.result
                        else None
                    ),
                }
                for critical in attack_result.criticals
            ]
        if attack_result.fumble:
            result_dict["fumble"] = {
                "status": attack_result.fumble.status,
                "roll": attack_result.fumble.roll,
                "text": attack_result.fumble.text,
            }
        return result_dict
