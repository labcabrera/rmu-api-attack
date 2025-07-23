"""
Attack web controller using hexagonal architecture.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.infrastructure.dependency_container import container
from app.infrastructure.adapters.web.attack_dtos import (
    AttackDTO,
    CreateAttackRequestDTO,
    AttackNotFoundDTO,
    attack_to_dto,
    create_request_to_domain
)

router = APIRouter(prefix="/attacks", tags=["attacks"])


@router.post("/", response_model=AttackDTO, status_code=201)
async def create_attack(request: CreateAttackRequestDTO):
    """Create a new attack"""
    try:
        create_use_case = container.get_create_attack_use_case()
        attack = create_request_to_domain(request)
        created_attack = await create_use_case.execute(
            attack_id=attack.id,
            tactical_game_id=attack.tactical_game_id,
            source_id=attack.input.source_id,
            target_id=attack.input.target_id,
            action_points=attack.input.action_points,
            mode=attack.input.mode
        )
        return attack_to_dto(created_attack)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{attack_id}", response_model=AttackDTO, responses={404: {"model": AttackNotFoundDTO}})
async def get_attack(attack_id: str):
    """Get attack by ID"""
    try:
        get_use_case = container.get_get_attack_use_case()
        attack = await get_use_case.execute(attack_id)
        
        if not attack:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id}
            )
            
        return attack_to_dto(attack)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[AttackDTO])
async def list_attacks(
    tactical_game_id: Optional[str] = Query(None, description="Filter by tactical game ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, description="Maximum number of results", ge=1, le=1000),
    skip: int = Query(0, description="Number of results to skip", ge=0)
):
    """List attacks with optional filters"""
    try:
        list_use_case = container.get_list_attacks_use_case()
        attacks = await list_use_case.execute(
            tactical_game_id=tactical_game_id,
            status=status,
            limit=limit,
            skip=skip
        )
        return [attack_to_dto(attack) for attack in attacks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{attack_id}", response_model=AttackDTO, responses={404: {"model": AttackNotFoundDTO}})
async def update_attack(attack_id: str, update_data: dict):
    """Update attack (partial update)"""
    try:
        update_use_case = container.get_update_attack_use_case()
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        attack = await update_use_case.execute(attack_id, update_data)
        
        if not attack:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id}
            )
            
        return attack_to_dto(attack)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{attack_id}", status_code=204)
async def delete_attack(attack_id: str):
    """Delete attack by ID"""
    try:
        delete_use_case = container.get_delete_attack_use_case()
        deleted = await delete_use_case.execute(attack_id)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{attack_id}/roll", response_model=AttackDTO, responses={404: {"model": AttackNotFoundDTO}})
async def execute_attack_roll(attack_id: str, roll_data: dict):
    """Execute attack roll"""
    try:
        roll_use_case = container.get_execute_attack_roll_use_case()
        roll_value = roll_data.get("roll")
        
        if roll_value is None:
            raise HTTPException(status_code=400, detail="Roll value is required")
        
        attack = await roll_use_case.execute(attack_id, roll_value)
        
        if not attack:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id}
            )
            
        return attack_to_dto(attack)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{attack_id}/results", response_model=AttackDTO, responses={404: {"model": AttackNotFoundDTO}})
async def apply_attack_results(attack_id: str, results_data: dict):
    """Apply attack results"""
    try:
        results_use_case = container.get_apply_attack_results_use_case()
        
        label = results_data.get("label")
        hit_points = results_data.get("hit_points", 0)
        criticals = results_data.get("criticals", [])
        
        if not label:
            raise HTTPException(status_code=400, detail="Result label is required")
        
        attack = await results_use_case.execute(attack_id, label, hit_points, criticals)
        
        if not attack:
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id}
            )
            
        return attack_to_dto(attack)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
                200: {"description": "Attack found successfully"},
                404: {"description": "Attack not found", "model": AttackNotFoundDTO}
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
        ) -> AttackDTO:
            attack = await self.get_attack_use_case.execute(attackId)
            
            if not attack:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "detail": "Attack not found",
                        "attack_id": attackId
                    }
                )
            
            return attack_to_dto(attack)

        @self.router.post(
            "/",
            response_model=AttackDTO,
            status_code=201,
            responses={
                201: {"description": "Attack created successfully"},
                400: {"description": "Invalid input data"},
                409: {"description": "Attack with this ID already exists"}
            },
            summary="Create a new attack",
            description="Creates a new attack in the system"
        )
        async def create_attack(request: CreateAttackRequestDTO) -> AttackDTO:
            try:
                attack = await self.create_attack_use_case.execute(
                    attack_id=request.id,
                    tactical_game_id=request.tacticalGameId,
                    source_id=request.sourceId,
                    target_id=request.targetId,
                    action_points=request.actionPoints,
                    mode=request.mode
                )
                return attack_to_dto(attack)
            except ValueError as e:
                raise HTTPException(status_code=409, detail=str(e))

        @self.router.patch(
            "/{attackId}",
            response_model=AttackDTO,
            responses={
                200: {"description": "Attack updated successfully"},
                404: {"description": "Attack not found", "model": AttackNotFoundDTO},
                400: {"description": "Invalid input data"}
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
        ) -> AttackDTO:
            updated_attack = await self.update_attack_use_case.execute(attackId, update_data)
            
            if not updated_attack:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "detail": "Attack not found",
                        "attack_id": attackId
                    }
                )
            
            return attack_to_dto(updated_attack)

        @self.router.delete(
            "/{attackId}",
            status_code=204,
            responses={
                204: {"description": "Attack deleted successfully"},
                404: {"description": "Attack not found", "model": AttackNotFoundDTO}
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
            deleted = await self.delete_attack_use_case.execute(attackId)
            
            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "detail": "Attack not found",
                        "attack_id": attackId
                    }
                )

        @self.router.get(
            "/",
            response_model=List[AttackDTO],
            responses={
                200: {"description": "Attacks retrieved successfully"}
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
        ) -> List[AttackDTO]:
            attacks = await self.list_attacks_use_case.execute(
                tactical_game_id=tactical_game_id,
                status=status,
                limit=limit,
                skip=skip
            )
            return [attack_to_dto(attack) for attack in attacks]
