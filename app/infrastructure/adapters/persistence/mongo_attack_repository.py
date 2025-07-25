"""
MongoDB adapter for attack persistence.
This is an infrastructure adapter that implements the AttackRepository port.
"""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from app.config import settings
from app.domain.ports import AttackRepository
from app.domain.entities import Attack
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
        await self.connect()
        try:
            object_id = ObjectId(attack_id)
            attack_dict = await self._collection.find_one({"_id": object_id})
            if attack_dict:
                return self._converter.dict_to_attack(attack_dict)
        except Exception:
            pass
        return None

    async def find_by_rsql(self, rsql_query: str) -> List[Attack]:
        """Find attacks by RSQL query"""
        await self.connect()
        try:
            cursor = self._collection.find({"$text": {"$search": rsql_query}})
            attacks = []
            async for doc in cursor:
                attacks.append(self._converter.dict_to_attack(doc))
            return attacks
        except Exception:
            return []

    async def save(self, attack: Attack) -> Attack:
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
        await self.connect()
        if not attack.id:
            raise ValueError("Cannot update attack without ID")
        try:
            object_id = ObjectId(attack.id)
            attack_dict = self._converter.attack_to_dict(attack, include_id=True)
            result = await self._collection.replace_one({"_id": object_id}, attack_dict)
            if result.matched_count == 0:
                return None
            return attack
        except Exception:
            return None

    async def delete(self, attack_id: str) -> bool:
        await self.connect()
        try:
            object_id = ObjectId(attack_id)
            result = await self._collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def exists(self, attack_id: str) -> bool:
        await self.connect()
        try:
            object_id = ObjectId(attack_id)
            count = await self._collection.count_documents({"_id": object_id})
            return count > 0
        except Exception:
            return False

    async def count_by_rsql(self, rsql_query: str) -> int:
        """Count attacks by RSQL query"""
        await self.connect()
        try:
            cursor = self._collection.find({"$text": {"$search": rsql_query}})
            count = await cursor.count()
            return count
        except Exception:
            return 0

    async def find_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Attack]:
        await self.connect()
        query = {}
        if action_id:
            query["action_id"] = action_id
        if source_id:
            query["source_id"] = source_id
        if target_id:
            query["target_id"] = target_id
        if status:
            query["status"] = status

        cursor = self._collection.find(query).skip(skip).limit(limit)
        attacks = []
        async for doc in cursor:
            attacks.append(self._converter.dict_to_attack(doc))
        return attacks

    async def count_all(
        self,
        action_id: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        await self.connect()
        query = {}
        if action_id:
            query["action_id"] = action_id
        if source_id:
            query["source_id"] = source_id
        if target_id:
            query["target_id"] = target_id
        if status:
            query["status"] = status

        return await self._collection.count_documents(query)
