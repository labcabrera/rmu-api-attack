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
from .mongo_attack_converter import MongoAttackConverter


class MongoAttackRepository(AttackRepository):
    """MongoDB implementation of AttackRepository"""

    def __init__(self, database=None):
        self._converter = MongoAttackConverter()

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

    async def find_by_id(self, attack_id: str) -> Optional[Attack]:
        """Find an attack by its ID"""
        await self.connect()

        try:
            # Convert string ID to ObjectId for MongoDB query
            object_id = ObjectId(attack_id)
            attack_dict = await self._collection.find_one({"_id": object_id})
            if attack_dict:
                return self._converter.dict_to_attack(attack_dict)
        except Exception:
            # Invalid ObjectId format
            pass

        return None

    async def find_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        """Find attacks with optional filters"""
        await self.connect()

        # Build filter query
        filter_query = {}
        if action_id:
            filter_query["action_id"] = action_id
        if source_id:
            filter_query["source_id"] = source_id
        if target_id:
            filter_query["target_id"] = target_id
        if status:
            filter_query["status"] = status

        cursor = self._collection.find(filter_query).skip(skip).limit(limit)
        attacks = []

        async for attack_dict in cursor:
            attack = self._converter.dict_to_attack(attack_dict)
            if attack:
                attacks.append(attack)

        return attacks

    async def count_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count attacks with optional filters"""
        await self.connect()

        # Build filter query (same as find_all)
        filter_query = {}
        if action_id:
            filter_query["action_id"] = action_id
        if source_id:
            filter_query["source_id"] = source_id
        if target_id:
            filter_query["target_id"] = target_id
        if status:
            filter_query["status"] = status

        return await self._collection.count_documents(filter_query)

    async def save(self, attack: Attack) -> Attack:
        """Save a new attack"""
        await self.connect()

        attack_dict = self._converter.attack_to_dict(attack, include_id=False)
        try:
            result = await self._collection.insert_one(attack_dict)
            return self._converter.dict_to_attack(
                {**attack_dict, "_id": result.inserted_id}
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
            attack_dict = self._converter.attack_to_dict(attack, include_id=True)

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
