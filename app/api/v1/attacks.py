from fastapi import APIRouter, HTTPException, Path
from app.models import Attack, AttackNotFound
from app.services import attack_service

router = APIRouter()

@router.get(
    "/{attackId}",
    response_model=Attack,
    responses={
        200: {
            "description": "Attack found successfully",
            "model": Attack
        },
        404: {
            "description": "Attack not found",
            "model": AttackNotFound
        }
    },
    summary="Get attack by ID",
    description="Gets the details of a specific attack using its unique identifier"
)
async def get_attack(
    attackId: str = Path(
        ...,
        description="Unique attack identifier",
        example="atk_001",
        min_length=1,
        max_length=50
    )
) -> Attack:
    """
    Gets the details of a specific attack.
    
    - **attackId**: The unique identifier of the attack to query
    
    Returns all attack information including:
    - Attack ID and name
    - Detailed description
    - Damage, accuracy and PP statistics
    - Attack type and element
    - Creation and last update dates
    """
    attack = await attack_service.get_attack_by_id(attackId)
    
    if not attack:
        raise HTTPException(
            status_code=404,
            detail={
                "detail": "Attack not found",
                "attack_id": attackId
            }
        )
    
    return attack
