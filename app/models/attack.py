from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class AttackMode(Enum):
    MAIN_HAND = "mainHand"
    OFF_HAND = "offHand"

class AttackInput(BaseModel):
    """Model for attack creation or update request"""
    
    model_config = ConfigDict(use_enum_values=True)
    
    sourceId: str = Field(..., description="Attack source identifier")
    targetId: str = Field(..., description="Attack target identifier")
    actionPoints: int = Field(..., description="Action points required to execute the attack")
    mode: AttackMode = Field(..., description="Attack mode (mainHand, offHand)")

class AttackRoll(BaseModel):
    """Model for attack roll resolution"""
    
    model_config = ConfigDict(use_enum_values=True)
    
    roll: int = Field(..., description="Random roll result for the attack")

class AttackResult(BaseModel):
    """Model for attack result"""
    
    model_config = ConfigDict(use_enum_values=True)
    
    labelResult: str = Field(..., description="Label indicating the result of the attack")
    hitPoints: int = Field(..., description="Hit points affected by the attack")
    criticals: list[dict] = Field(..., description="List of critical hits associated with the attack")

class Attack(BaseModel):
    """Model representing an attack in the RMU system"""
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
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
                    "roll": 12
                },
                "results": {
                    "labelResult": "5AT",
                    "hitPoints": 5,
                    "criticals": [
                        {
                            "id": "crit_001",
                            "status": "pending"
                        }
                    ]
                }
            }
        }
    )
    
    id: str = Field(..., description="Unique attack identifier")
    tacticalGameId: str = Field(..., description="Tactical game identifier to which the attack belongs")
    status: str = Field(..., description="Current status of the attack (e.g., pending, executed)")
    input: AttackInput = Field(..., description="Attack input data")
    roll: Optional[AttackRoll] = Field(None, description="Attack roll resolution data")
    results: Optional[AttackResult] = Field(None, description="Results of the attack execution")

class BonusModifier(BaseModel):
    """Model representing a bonus modifier for an attack"""
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "type": "critical",
                "value": 20
            }
        }
    )

    type: str = Field(..., description="Bonus type (e.g., critical, elemental advantage, etc.)")
    value: int = Field(..., description="Numeric bonus value")

class AttackNotFound(BaseModel):
    """Response model when an attack is not found"""
    
    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "detail": "Attack not found",
                "attack_id": "atk_999"
            }
        }
    )
    
    detail: str = Field(..., description="Error message")
    attack_id: str = Field(..., description="ID of the attack that was not found")

