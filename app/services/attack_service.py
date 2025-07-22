from typing import Optional, Dict, Any
from datetime import datetime
from app.models.attack import Attack

class AttackService:
    """Service to manage attack-related operations"""
    
    def __init__(self):
        # Simulate an in-memory database with some example attacks
        self._attacks_db: Dict[str, Dict[str, Any]] = {
            "atk_001": {
                "id": "atk_001",
                "tacticalGameId": "game_001",
                "status": "executed",
                "input": {
                    "sourceId": "source_001",
                    "targetId": "target_001",
                    "actionPoints": 3,
                    "mode": "mainHand"
                },
                "roll": {
                    "roll": 15
                },
                "results": {
                    "labelResult": "8AT",
                    "hitPoints": 8,
                    "criticals": [
                        {
                            "id": "crit_001",
                            "status": "applied"
                        }
                    ]
                }
            },
            "atk_002": {
                "id": "atk_002",
                "tacticalGameId": "game_002",
                "status": "pending",
                "input": {
                    "sourceId": "source_002",
                    "targetId": "target_002",
                    "actionPoints": 4,
                    "mode": "offHand"
                },
                "roll": None,
                "results": None
            }
        }
    
    async def get_attack_by_id(self, attack_id: str) -> Optional[Attack]:
        """
        Gets an attack by its ID
        
        Args:
            attack_id: Unique attack ID
            
        Returns:
            Attack if found, None if it doesn't exist
        """
        attack_data = self._attacks_db.get(attack_id)
        if attack_data:
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
        return attack_id in self._attacks_db

# Singleton service instance
attack_service = AttackService()
