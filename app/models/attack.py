from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Attack(BaseModel):
    """Model representing an attack in the RMU system"""
    
    id: str = Field(..., description="Unique attack identifier")
    tacticalGameId: str = Field(..., description="Tactical game identifier to which the attack belongs")
    actionPoints: int = Field(..., description="Action points required to execute the attack")
    mode: str = Field(..., description="Attack mode (physical, magical, special)")

    # name: str = Field(..., description="Attack name")
    # description: str = Field(..., description="Detailed attack description")
    # damage: int = Field(..., ge=0, description="Base attack damage")
    # attack_type: str = Field(..., description="Attack type (physical, magical, special)")
    # element: Optional[str] = Field(None, description="Attack element (fire, water, earth, air, etc.)")
    # accuracy: int = Field(100, ge=0, le=100, description="Attack accuracy (0-100)")
    # pp: int = Field(..., ge=1, description="Power points (available uses)")
    # created_at: datetime = Field(default_factory=datetime.now, description="Creation date")
    # updated_at: Optional[datetime] = Field(None, description="Last update date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "atk_001",
                "requestData":{
                    "tacticalGameId": "game_001",
                    "sourceId": "source_001",
                    "targetId": "target_001",
                    "actionPoints": 3,
                    "mode": "mainHand"
                },
                "resolutionData": {
                    "roll": 12
                },
                "results": {
                    "labelResult": "5AT",
                    "hitPoints": 5,
                    "criticals": [
                        {
                            "id": "foo",
                            "status": "pending"
                        }
                    ]
                },
                "name": "Fireball",
                "description": "A powerful magical attack that launches a sphere of fire",
                "damage": 85,
                "attack_type": "magical",
                "element": "fire",
                "accuracy": 95,
                "pp": 15,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }

class AttackRequestData(BaseModel):
    """Model for attack creation or update request"""
    
    tacticalGameId: str = Field(..., description="Tactical game identifier to which the attack belongs")
    sourceId: str = Field(..., description="Attack source identifier")
    targetId: str = Field(..., description="Attack target identifier")
    actionPoints: int = Field(..., description="Action points required to execute the attack")
    mode: str = Field(..., description="Attack mode (physical, magical, special)")


    name: str = Field(..., description="Attack name")
    description: str = Field(..., description="Detailed attack description")
    damage: int = Field(..., ge=0, description="Base attack damage")
    attack_type: str = Field(..., description="Attack type (physical, magical, special)")
    element: Optional[str] = Field(None, description="Attack element (fire, water, earth, air, etc.)")
    accuracy: int = Field(100, ge=0, le=100, description="Attack accuracy (0-100)")
    pp: int = Field(..., ge=1, description="Power points (available uses)")


class BonusModifier(BaseModel):
    """Model representing a bonus modifier for an attack"""

    type: str = Field(..., description="Bonus type (e.g., critical, elemental advantage, etc.)")
    value: int = Field(..., description="Numeric bonus value")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "critical",
                "value": 20
            }
        }

class AttackNotFound(BaseModel):
    """Response model when an attack is not found"""
    
    detail: str = Field(..., description="Error message")
    attack_id: str = Field(..., description="ID of the attack that was not found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Attack not found",
                "attack_id": "atk_999"
            }
        }
