from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from app.config import settings
from app.models.attack import Attack, AttackInput, AttackRoll, AttackResult

class AttackService:
    """Service to manage attack-related operations using MongoDB"""
    
    def __init__(self):
        # MongoDB connection configuration
        self.mongo_url = settings.MONGODB_URL
        self.database_name = settings.MONGODB_DATABASE
        self.collection_name = "attacks"
        
        self._client: Optional[AsyncIOMotorClient] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    async def connect(self):
        """Initialize MongoDB connection"""
        if not self._client:
            self._client = AsyncIOMotorClient(self.mongo_url)
            self._database = self._client[self.database_name]
            self._collection = self._database[self.collection_name]
            
            # Ensure index on id field
            await self._collection.create_index("id", unique=True)
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            self._collection = None
    
    async def get_attack_by_id(self, attack_id: str) -> Optional[Attack]:
        """
        Gets an attack by its ID
        
        Args:
            attack_id: Unique attack ID
            
        Returns:
            Attack if found, None if it doesn't exist
        """
        await self.connect()
        
        attack_data = await self._collection.find_one({"id": attack_id})
        if attack_data:
            # Remove MongoDB's _id field
            attack_data.pop("_id", None)
            return Attack(**attack_data)
        return None
    
    async def attack_exists(self, attack_id: str) -> bool:
        """
        Verifies if an attack with the given ID exists
        
        Args:
            attack_id: Unique attack ID
            
        Returns:
            True if it exists, False if not
        """
        await self.connect()
        
        count = await self._collection.count_documents({"id": attack_id})
        return count > 0
    
    async def create_attack(self, attack: Attack) -> Attack:
        """
        Creates a new attack
        
        Args:
            attack: Attack object to create
            
        Returns:
            Created Attack object
            
        Raises:
            ValueError: If attack already exists
        """
        await self.connect()
        
        attack_dict = attack.model_dump()
        
        try:
            await self._collection.insert_one(attack_dict)
            return attack
        except DuplicateKeyError:
            raise ValueError(f"Attack with ID {attack.id} already exists")
    
    async def update_attack_partial(self, attack_id: str, update_data: Dict[str, Any]) -> Optional[Attack]:
        """
        Partially updates an attack (PATCH operation)
        
        Args:
            attack_id: Unique attack ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Attack if found and updated, None if not found
        """
        await self.connect()
        
        # Filter out None values and empty dictionaries
        filtered_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not filtered_data:
            return await self.get_attack_by_id(attack_id)
        
        result = await self._collection.update_one(
            {"id": attack_id},
            {"$set": filtered_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_attack_by_id(attack_id)
    
    async def update_attack_full(self, attack_id: str, attack: Attack) -> Optional[Attack]:
        """
        Fully replaces an attack (PUT operation)
        
        Args:
            attack_id: Unique attack ID
            attack: Complete Attack object to replace with
            
        Returns:
            Updated Attack if found and updated, None if not found
        """
        await self.connect()
        
        attack_dict = attack.model_dump()
        
        result = await self._collection.replace_one(
            {"id": attack_id},
            attack_dict
        )
        
        if result.matched_count == 0:
            return None
        
        return attack
    
    async def delete_attack(self, attack_id: str) -> bool:
        """
        Deletes an attack
        
        Args:
            attack_id: Unique attack ID
            
        Returns:
            True if deleted, False if not found
        """
        await self.connect()
        
        result = await self._collection.delete_one({"id": attack_id})
        return result.deleted_count > 0
    
    async def list_attacks(self, tactical_game_id: Optional[str] = None, 
                          status: Optional[str] = None, 
                          limit: int = 100, 
                          skip: int = 0) -> list[Attack]:
        """
        Lists attacks with optional filters
        
        Args:
            tactical_game_id: Filter by tactical game ID
            status: Filter by status
            limit: Maximum number of attacks to return
            skip: Number of attacks to skip
            
        Returns:
            List of Attack objects
        """
        await self.connect()
        
        # Build filter query
        filter_query = {}
        if tactical_game_id:
            filter_query["tacticalGameId"] = tactical_game_id
        if status:
            filter_query["status"] = status
        
        cursor = self._collection.find(filter_query).skip(skip).limit(limit)
        attacks = []
        
        async for attack_data in cursor:
            attack_data.pop("_id", None)
            attacks.append(Attack(**attack_data))
        
        return attacks

# Singleton service instance
attack_service = AttackService()
