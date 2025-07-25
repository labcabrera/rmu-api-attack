"""
MongoDB adapter for Critical repository.
"""

from typing import Optional, List, Dict, Any
from pymongo.errors import DuplicateKeyError
from app.domain.entities.critical import Critical
from app.domain.ports.critical_ports import CriticalRepository


class MongoCriticalRepository(CriticalRepository):
    """MongoDB implementation of CriticalRepository"""

    def __init__(self, database):
        self._database = database
        self._collection = database.criticals

    async def initialize(self):
        """Initialize the repository with indexes"""
        # Create unique index on id field
        await self._collection.create_index("id", unique=True)
        # Create index on status for filtering
        await self._collection.create_index("status")
        # Create index on type for filtering
        await self._collection.create_index("type")

    def _critical_to_dict(self, critical: Critical) -> Dict[str, Any]:
        """Convert Critical entity to dictionary for MongoDB storage"""
        return {
            "id": critical.id,
            "type": critical.type,
            "roll": critical.roll,
            "result": critical.result,
            "status": critical.status,
        }

    def _dict_to_critical(self, critical_dict: Dict[str, Any]) -> Optional[Critical]:
        """Convert dictionary from MongoDB to Critical entity"""
        if not critical_dict:
            return None

        # Remove MongoDB's _id field if present
        critical_dict.pop("_id", None)

        return Critical(
            id=critical_dict["id"],
            type=critical_dict["type"],
            roll=critical_dict["roll"],
            result=critical_dict["result"],
            status=critical_dict["status"],
        )

    async def save(self, critical: Critical) -> Critical:
        """Save a critical to MongoDB"""
        critical_dict = self._critical_to_dict(critical)

        try:
            await self._collection.insert_one(critical_dict)
            return critical
        except DuplicateKeyError:
            raise ValueError(f"Critical with ID {critical.id} already exists")

    async def find_by_id(self, critical_id: str) -> Optional[Critical]:
        """Find a critical by ID"""
        critical_dict = await self._collection.find_one({"id": critical_id})
        return self._dict_to_critical(critical_dict)

    async def update(self, critical: Critical) -> Optional[Critical]:
        """Update a critical in MongoDB"""
        critical_dict = self._critical_to_dict(critical)

        result = await self._collection.replace_one({"id": critical.id}, critical_dict)

        if result.matched_count > 0:
            return critical
        return None

    async def delete(self, critical_id: str) -> bool:
        """Delete a critical by ID"""
        result = await self._collection.delete_one({"id": critical_id})
        return result.deleted_count > 0

    async def find_all(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[Critical]:
        """Find criticals with optional filters"""
        query = {}
        if status:
            query["status"] = status
        if type:
            query["type"] = type

        cursor = self._collection.find(query).skip(skip).limit(limit)
        criticals = []

        async for critical_dict in cursor:
            critical = self._dict_to_critical(critical_dict)
            if critical:
                criticals.append(critical)

        return criticals

    async def exists(self, critical_id: str) -> bool:
        """Check if a critical exists"""
        count = await self._collection.count_documents({"id": critical_id})
        return count > 0
