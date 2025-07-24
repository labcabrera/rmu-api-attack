"""
MongoDB adapter for attack persistence.
This is an infrastructure adapter that implements the AttackRepository port.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.config import settings
from app.domain.ports import AttackRepository
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


class MongoAttackRepository(AttackRepository):
    """MongoDB implementation of AttackRepository"""

    def __init__(self, database=None):
        if database is not None:
            # Use provided database connection (from container)
            self._client = None
            self._database = database
            self._collection = database.attacks
        else:
            # Create own connection (legacy mode)
            self.mongo_url = settings.MONGODB_URL
            self.database_name = settings.MONGODB_DATABASE
            self.collection_name = "attacks"

            self._client = None
            self._database = None
            self._collection = None

    async def connect(self):
        """Initialize MongoDB connection"""
        if self._database is not None:
            return

        if not self._client:
            self._client = AsyncIOMotorClient(self.mongo_url)
            self._database = self._client[self.database_name]
            self._collection = self._database[self.collection_name]

    async def disconnect(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._collection = None

    def _attack_to_dict(self, attack: Attack) -> Dict[str, Any]:
        """Convert Attack domain entity to dictionary for MongoDB"""

        status_str = (
            attack.status.value
            if isinstance(attack.status, AttackStatus)
            else attack.status
        )

        attack_dict = {
            "actionId": attack.action_id,
            "sourceId": attack.source_id,
            "targetId": attack.target_id,
            "status": status_str,
            "modifiers": {
                "attack_type": "melee",
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

        # Add _id if attack has an id (for updates)
        if attack.id:
            attack_dict["_id"] = ObjectId(attack.id)

        if attack.roll:
            attack_dict["roll"] = {"roll": attack.roll.roll}
        else:
            attack_dict["roll"] = None

        if attack.results:
            attack_dict["results"] = {
                "label_result": attack.results.label_result,
                "hit_points": attack.results.hit_points,
                "criticals": [
                    {"id": c.id, "status": c.status} for c in attack.results.criticals
                ],
            }
        else:
            attack_dict["results"] = None

        return attack_dict

    def _dict_to_attack(self, attack_dict: Dict[str, Any]) -> Attack:
        """Convert dictionary from MongoDB to Attack domain entity"""
        if not attack_dict:
            return None

        # Convert MongoDB's _id to string for domain entity
        attack_id = str(attack_dict["_id"])

        # Convert input
        input_data = attack_dict["input"]
        modifiers = AttackModifiers(
            # TODO
            attack_type=AttackType.MELEE,
            rollModifiers=AttackRollModifiers(
                bo=input_data["roll_modifiers"]["bo"],
                bo_injury_penalty=input_data["roll_modifiers"].get(
                    "bo_injury_penalty", 0
                ),
                bo_actions_points_penalty=input_data["roll_modifiers"].get(
                    "bo_actions_points_penalty", 0
                ),
                bo_pace_penalty=input_data["roll_modifiers"].get("bo_pace_penalty", 0),
                bo_fatigue_penalty=input_data["roll_modifiers"].get(
                    "bo_fatigue_penalty", 0
                ),
                bd=input_data["roll_modifiers"]["bd"],
                range_penalty=input_data["roll_modifiers"].get("range_penalty", 0),
                parry=input_data["roll_modifiers"].get("parry", 0),
                custom_bonus=input_data["roll_modifiers"].get("custom_bonus", 0),
            ),
            round=input_data["round"],
            mode=AttackMode(input_data["mode"]),
        )

        # Convert roll
        roll = None
        if attack_dict.get("roll"):
            roll = AttackRoll(roll=attack_dict["roll"]["roll"])

        # Convert results
        results = None
        if attack_dict.get("results"):
            results_data = attack_dict["results"]
            criticals = [
                Critical(id=c["id"], status=c["status"])
                for c in results_data.get("criticals", [])
            ]
            results = AttackResult(
                label_result=results_data["label_result"],
                hit_points=results_data["hit_points"],
                criticals=criticals,
            )

        return Attack(
            id=attack_id,
            action_id=attack_dict["actionId"],
            source_id=attack_dict["sourceId"],
            target_id=attack_dict["targetId"],
            modifiers=modifiers,
            # TODO
            status=attack_dict["status"],
            roll=roll,
            results=results,
        )

    async def find_by_id(self, attack_id: str) -> Optional[Attack]:
        """Find an attack by its ID"""
        await self.connect()

        try:
            # Convert string ID to ObjectId for MongoDB query
            object_id = ObjectId(attack_id)
            attack_dict = await self._collection.find_one({"_id": object_id})
            if attack_dict:
                return self._dict_to_attack(attack_dict)
        except Exception:
            # Invalid ObjectId format
            pass

        return None

    async def save(self, attack: Attack) -> Attack:
        """Save a new attack"""
        await self.connect()

        # Convert to dict (without _id for new documents)
        attack_dict = self._attack_to_dict(attack)

        try:
            # Insert and get the generated _id
            result = await self._collection.insert_one(attack_dict)

            # Return attack with the generated MongoDB _id
            return Attack(
                id=str(result.inserted_id),
                source_id=attack.source_id,
                target_id=attack.target_id,
                modifiers=attack.modifiers,
                roll=attack.roll,
                results=attack.results,
            )

        except DuplicateKeyError:
            raise ValueError(f"Attack with ID {attack.id} already exists")

    async def update(self, attack: Attack) -> Optional[Attack]:
        """Update an existing attack"""
        await self.connect()

        # Attack must have an ID for updates
        if not attack.id:
            raise ValueError("Cannot update attack without ID")

        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(attack.id)
            attack_dict = self._attack_to_dict(attack)

            result = await self._collection.replace_one({"_id": object_id}, attack_dict)

            if result.matched_count == 0:
                return None

            return attack

        except Exception:
            # Invalid ObjectId format
            return None

    async def delete(self, attack_id: str) -> bool:
        """Delete an attack by its ID"""
        await self.connect()

        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(attack_id)
            result = await self._collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            # Invalid ObjectId format
            return False

    async def find_all(
        self,
        tactical_game_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Find attacks with optional filters"""
        await self.connect()

        # Build filter query
        filter_query = {}
        if tactical_game_id:
            filter_query["tactical_game_id"] = tactical_game_id
        if status:
            filter_query["status"] = status

        cursor = self._collection.find(filter_query).skip(skip).limit(limit)
        attacks = []

        async for attack_dict in cursor:
            attack = self._dict_to_attack(attack_dict)
            if attack:
                attacks.append(attack)

        return attacks

    async def exists(self, attack_id: str) -> bool:
        """Check if an attack exists"""
        await self.connect()

        try:
            # Convert string ID to ObjectId
            object_id = ObjectId(attack_id)
            count = await self._collection.count_documents({"_id": object_id})
            return count > 0
        except Exception:
            # Invalid ObjectId format
            return False
