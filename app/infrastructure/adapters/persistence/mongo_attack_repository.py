"""
MongoDB adapter for attack persistence.
This is an infrastructure adapter that implements the AttackRepository port.
"""

from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError

from app.domain.entities import Attack, AttackInput, AttackRoll, AttackResult, AttackMode, Critical
from app.domain.ports import AttackRepository
from app.config import settings


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
            # Already connected via container
            return
        
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
    
    def _attack_to_dict(self, attack: Attack) -> Dict[str, Any]:
        """Convert Attack domain entity to dictionary for MongoDB"""
        attack_dict = {
            "id": attack.id,
            "tactical_game_id": attack.tactical_game_id,
            "status": attack.status,
            "input": {
                "source_id": attack.input.source_id,
                "target_id": attack.input.target_id,
                "action_points": attack.input.action_points,
                "mode": attack.input.mode.value
            }
        }
        
        if attack.roll:
            attack_dict["roll"] = {"roll": attack.roll.roll}
        else:
            attack_dict["roll"] = None
            
        if attack.results:
            attack_dict["results"] = {
                "label_result": attack.results.label_result,
                "hit_points": attack.results.hit_points,
                "criticals": [
                    {"id": c.id, "status": c.status} 
                    for c in attack.results.criticals
                ]
            }
        else:
            attack_dict["results"] = None
            
        return attack_dict
    
    def _dict_to_attack(self, attack_dict: Dict[str, Any]) -> Attack:
        """Convert dictionary from MongoDB to Attack domain entity"""
        if not attack_dict:
            return None
            
        # Remove MongoDB's _id field
        attack_dict.pop("_id", None)
        
        # Convert input
        input_data = attack_dict["input"]
        attack_input = AttackInput(
            source_id=input_data["source_id"],
            target_id=input_data["target_id"], 
            action_points=input_data["action_points"],
            mode=AttackMode(input_data["mode"])
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
                criticals=criticals
            )
        
        return Attack(
            id=attack_dict["id"],
            tactical_game_id=attack_dict["tactical_game_id"],
            status=attack_dict["status"],
            input=attack_input,
            roll=roll,
            results=results
        )
    
    async def find_by_id(self, attack_id: str) -> Optional[Attack]:
        """Find an attack by its ID"""
        await self.connect()
        
        attack_dict = await self._collection.find_one({"id": attack_id})
        if attack_dict:
            return self._dict_to_attack(attack_dict)
        return None
    
    async def save(self, attack: Attack) -> Attack:
        """Save a new attack"""
        await self.connect()
        
        attack_dict = self._attack_to_dict(attack)
        
        try:
            await self._collection.insert_one(attack_dict)
            return attack
        except DuplicateKeyError:
            raise ValueError(f"Attack with ID {attack.id} already exists")
    
    async def update(self, attack: Attack) -> Optional[Attack]:
        """Update an existing attack"""
        await self.connect()
        
        attack_dict = self._attack_to_dict(attack)
        
        result = await self._collection.replace_one(
            {"id": attack.id},
            attack_dict
        )
        
        if result.matched_count == 0:
            return None
        
        return attack
    
    async def delete(self, attack_id: str) -> bool:
        """Delete an attack by its ID"""
        await self.connect()
        
        result = await self._collection.delete_one({"id": attack_id})
        return result.deleted_count > 0
    
    async def find_all(self, tactical_game_id: Optional[str] = None,
                      status: Optional[str] = None,
                      limit: int = 100, 
                      skip: int = 0) -> List[Attack]:
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
        
        count = await self._collection.count_documents({"id": attack_id})
        return count > 0
