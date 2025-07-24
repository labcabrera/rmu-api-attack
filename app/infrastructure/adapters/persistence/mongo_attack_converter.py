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
    AttackMode,
    Critical,
    AttackRollModifiers,
)
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
            "action_id": attack.action_id,
            "source_id": attack.source_id,
            "target_id": attack.target_id,
            "status": status_str,
            "modifiers": {
                "attack_type": attack_type_str,
                "roll_modifiers": {
                    "bo": attack.modifiers.roll_modifiers.bo,
                    "bo_injury_penalty": attack.modifiers.roll_modifiers.bo_injury_penalty,
                    "bo_actions_points_penalty": attack.modifiers.roll_modifiers.bo_actions_points_penalty,
                    "bo_pace_penalty": attack.modifiers.roll_modifiers.bo_pace_penalty,
                    "bo_fatigue_penalty": attack.modifiers.roll_modifiers.bo_fatigue_penalty,
                    "bd": attack.modifiers.roll_modifiers.bd,
                    "range_penalty": attack.modifiers.roll_modifiers.range_penalty,
                    "parry": attack.modifiers.roll_modifiers.parry,
                    "custom_bonus": attack.modifiers.roll_modifiers.custom_bonus,
                },
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

        # Handle results conversion
        if attack.results:
            attack_dict["results"] = {
                "label_result": attack.results.label_result,
                "hit_points": attack.results.hit_points,
                "criticals": [
                    {
                        "id": c.id,
                        "type": c.type,
                        "roll": c.roll,
                        "result": c.result,
                        "status": c.status,
                    }
                    for c in attack.results.criticals
                ],
            }
        else:
            attack_dict["results"] = None

        return attack_dict

    @staticmethod
    def dict_to_attack(attack_dict: Dict[str, Any]) -> Optional[Attack]:
        """Convert dictionary from MongoDB to Attack domain entity"""
        if not attack_dict:
            return None

        # Convert MongoDB's _id to string for domain entity
        attack_id = str(attack_dict["_id"])

        # Convert modifiers
        modifiers_data = attack_dict.get("modifiers", {})

        # Handle attack_type conversion (string to enum)
        attack_type = AttackType.MELEE  # default
        if "attack_type" in modifiers_data:
            try:
                attack_type = AttackType(modifiers_data["attack_type"])
            except ValueError:
                attack_type = AttackType.MELEE  # fallback to default

        # Convert roll_modifiers
        roll_modifiers_data = modifiers_data.get("roll_modifiers", {})
        roll_modifiers = AttackRollModifiers(
            bo=roll_modifiers_data.get("bo", 0),
            bo_injury_penalty=roll_modifiers_data.get("bo_injury_penalty", 0),
            bo_actions_points_penalty=roll_modifiers_data.get(
                "bo_actions_points_penalty", 0
            ),
            bo_pace_penalty=roll_modifiers_data.get("bo_pace_penalty", 0),
            bo_fatigue_penalty=roll_modifiers_data.get("bo_fatigue_penalty", 0),
            bd=roll_modifiers_data.get("bd", 0),
            range_penalty=roll_modifiers_data.get("range_penalty", 0),
            parry=roll_modifiers_data.get("parry", 0),
            custom_bonus=roll_modifiers_data.get("custom_bonus", 0),
        )

        modifiers = AttackModifiers(
            attack_type=attack_type,
            roll_modifiers=roll_modifiers,
        )

        # Convert roll
        roll = None
        if attack_dict.get("roll"):
            roll = AttackRoll(roll=attack_dict["roll"]["roll"])

        # Convert results
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

            results = AttackResult(
                label_result=results_data["label_result"],
                hit_points=results_data["hit_points"],
                criticals=criticals,
            )

        # Handle status conversion (string to enum)
        status = AttackStatus.DRAFT  # default
        if "status" in attack_dict:
            try:
                status = AttackStatus(attack_dict["status"])
            except ValueError:
                status = AttackStatus.DRAFT  # fallback to default

        return Attack(
            id=attack_id,
            tactical_game_id=attack_dict.get("tactical_game_id", ""),
            status=status,
            modifiers=modifiers,
            roll=roll,
            results=results,
        )
