from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Path, Query
from app.models.attack import Attack, AttackNotFound, AttackInput, AttackRoll, AttackResult
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
    - Attack ID and tactical game ID
    - Attack status and input data
    - Roll results and attack outcomes
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

@router.post(
    "/",
    response_model=Attack,
    status_code=201,
    responses={
        201: {
            "description": "Attack created successfully",
            "model": Attack
        },
        400: {
            "description": "Invalid input data"
        },
        409: {
            "description": "Attack with this ID already exists"
        }
    },
    summary="Create a new attack",
    description="Creates a new attack in the system"
)
async def create_attack(attack: Attack) -> Attack:
    """
    Creates a new attack in the system.
    
    The attack must include all required fields:
    - **id**: Unique identifier for the attack
    - **tacticalGameId**: ID of the tactical game
    - **status**: Current status of the attack
    - **input**: Attack input data
    """
    try:
        return await attack_service.create_attack(attack)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.patch(
    "/{attackId}",
    response_model=Attack,
    responses={
        200: {
            "description": "Attack updated successfully",
            "model": Attack
        },
        404: {
            "description": "Attack not found",
            "model": AttackNotFound
        },
        400: {
            "description": "Invalid input data"
        }
    },
    summary="Partially update an attack",
    description="Updates specific fields of an existing attack (PATCH operation)"
)
async def patch_attack(
    attackId: str = Path(
        ...,
        description="Unique attack identifier",
        example="atk_001",
        min_length=1,
        max_length=50
    ),
    update_data: Dict[str, Any] = ...
) -> Attack:
    """
    Partially updates an existing attack.
    
    - **attackId**: The unique identifier of the attack to update
    - **update_data**: Dictionary containing only the fields to update
    
    You can update any combination of:
    - **status**: Attack status
    - **roll**: Roll information
    - **results**: Attack results
    - **input**: Input parameters (partial updates supported)
    """
    updated_attack = await attack_service.update_attack_partial(attackId, update_data)
    
    if not updated_attack:
        raise HTTPException(
            status_code=404,
            detail={
                "detail": "Attack not found",
                "attack_id": attackId
            }
        )
    
    return updated_attack

@router.delete(
    "/{attackId}",
    status_code=204,
    responses={
        204: {
            "description": "Attack deleted successfully"
        },
        404: {
            "description": "Attack not found",
            "model": AttackNotFound
        }
    },
    summary="Delete an attack",
    description="Deletes an attack from the system"
)
async def delete_attack(
    attackId: str = Path(
        ...,
        description="Unique attack identifier",
        example="atk_001",
        min_length=1,
        max_length=50
    )
):
    """
    Deletes an attack from the system.
    
    - **attackId**: The unique identifier of the attack to delete
    """
    deleted = await attack_service.delete_attack(attackId)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "detail": "Attack not found",
                "attack_id": attackId
            }
        )

@router.get(
    "/",
    response_model=List[Attack],
    responses={
        200: {
            "description": "Attacks retrieved successfully",
            "model": List[Attack]
        }
    },
    summary="List attacks",
    description="Retrieves a list of attacks with optional filtering"
)
async def list_attacks(
    tactical_game_id: Optional[str] = Query(
        None,
        description="Filter by tactical game ID",
        example="game_001"
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by attack status",
        example="executed"
    ),
    limit: int = Query(
        100,
        description="Maximum number of attacks to return",
        ge=1,
        le=1000
    ),
    skip: int = Query(
        0,
        description="Number of attacks to skip",
        ge=0
    )
) -> List[Attack]:
    """
    Retrieves a list of attacks with optional filtering.
    
    - **tactical_game_id**: Filter attacks by tactical game ID
    - **status**: Filter attacks by status
    - **limit**: Maximum number of attacks to return (1-1000)
    - **skip**: Number of attacks to skip for pagination
    """
    return await attack_service.list_attacks(
        tactical_game_id=tactical_game_id,
        status=status,
        limit=limit,
        skip=skip
    )
