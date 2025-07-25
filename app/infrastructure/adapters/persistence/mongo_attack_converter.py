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
    Critical,
    AttackRollModifiers,
    AttackCalculations,
    AttackBonusEntry,
)
from app.domain.entities.attack_table import AttackTableEntry
from app.domain.entities.enums import AttackStatus, AttackType


class MongoAttackConverter:
    """Converter for Attack entities to/from MongoDB documents"""

    @staticmethod
    def attack_to_dict(attack: Attack, include_id: bool = True) -> Dict[str, Any]:
        """Convert Attack domain entity to dictionary for MongoDB"""

        # Handle status conversion (enum to string)
        status_str = (
            attack.status.value
            if isinstance(attack.status, AttackStatus)
            else attack.status
        )

        # Handle attack_type conversion (enum to string)
        attack_type_str = (
            attack.modifiers.attack_type.value
            if hasattr(attack.modifiers, "attack_type")
            and isinstance(attack.modifiers.attack_type, AttackType)
            else "melee"  # default value
        )

        attack_dict = {
            "actionId": attack.action_id,
            "sourceId": attack.source_id,
            "targetId": attack.target_id,
            "status": status_str,
            "modifiers": {
                "attackType": attack_type_str,
                "attackTable": attack.modifiers.attack_table,
                "attackSize": attack.modifiers.attack_size,
                "at": attack.modifiers.at,
                "rollModifiers": {
                    "bo": attack.modifiers.roll_modifiers.bo,
                    "boInjuryPenalty": attack.modifiers.roll_modifiers.bo_injury_penalty,
                    "boActionsPointsPenalty": attack.modifiers.roll_modifiers.bo_actions_points_penalty,
                    "boPacePenalty": attack.modifiers.roll_modifiers.bo_pace_penalty,
                    "boFatiguePenalty": attack.modifiers.roll_modifiers.bo_fatigue_penalty,
                    "bd": attack.modifiers.roll_modifiers.bd,
                    "rangePenalty": attack.modifiers.roll_modifiers.range_penalty,
                    "parry": attack.modifiers.roll_modifiers.parry,
                    "customBonus": attack.modifiers.roll_modifiers.custom_bonus,
                },
                "attackTable": attack.modifiers.attack_table,
                "attackSize": attack.modifiers.attack_size,
                "at": attack.modifiers.at,
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
                    "roll": attack.results.attack_table_entry.roll,
                    "at": attack.results.attack_table_entry.at,
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

        attack_type = AttackType.MELEE
        if "attack_type" in modifiers_data:
            try:
                attack_type = AttackType(modifiers_data["attackType"])
            except ValueError:
                attack_type = AttackType.MELEE  # fallback to default

        roll_modifiers_data = modifiers_data.get("rollModifiers", {})
        roll_modifiers = AttackRollModifiers(
            bo=roll_modifiers_data.get("bo", 0),
            bo_injury_penalty=roll_modifiers_data.get("boInjuryPenalty", 0),
            bo_actions_points_penalty=roll_modifiers_data.get(
                "boActionsPointsPenalty", 0
            ),
            bo_pace_penalty=roll_modifiers_data.get("boPacePenalty", 0),
            bo_fatigue_penalty=roll_modifiers_data.get("boFatiguePenalty", 0),
            bd=roll_modifiers_data.get("bd", 0),
            range_penalty=roll_modifiers_data.get("rangePenalty", 0),
            parry=roll_modifiers_data.get("parry", 0),
            custom_bonus=roll_modifiers_data.get("customBonus", 0),
        )

        modifiers = AttackModifiers(
            attack_type=attack_type,
            roll_modifiers=roll_modifiers,
            attack_table=attack_dict.get("modifiers", {}).get("attackTable", ""),
            attack_size=attack_dict.get("modifiers", {}).get("attackSize", ""),
            at=attack_dict.get("modifiers", {}).get("at", 0),
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
                critical = Critical(
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
                    roll=entry_data["roll"],
                    at=entry_data["at"],
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
