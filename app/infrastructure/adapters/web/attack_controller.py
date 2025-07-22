"""
Web controller for attacks using hexagonal architecture.
This adapter converts HTTP requests to use case calls.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Path, Query

from app.application.use_cases import (
    CreateAttackUseCase,
    GetAttackUseCase,
    ListAttacksUseCase,
    UpdateAttackUseCase,
    DeleteAttackUseCase
)
from app.infrastructure.adapters.web.attack_dtos import (
    AttackDTO,
    CreateAttackRequestDTO, 
    AttackNotFoundDTO,
    attack_to_dto,
    create_request_to_domain
)
from app.domain.entities import AttackMode


class AttackController:
    """Attack controller using hexagonal architecture"""
    
    def __init__(self,
                 create_attack_use_case: CreateAttackUseCase,
                 get_attack_use_case: GetAttackUseCase,
                 list_attacks_use_case: ListAttacksUseCase,
                 update_attack_use_case: UpdateAttackUseCase,
                 delete_attack_use_case: DeleteAttackUseCase):
        self.create_attack_use_case = create_attack_use_case
        self.get_attack_use_case = get_attack_use_case
        self.list_attacks_use_case = list_attacks_use_case
        self.update_attack_use_case = update_attack_use_case
        self.delete_attack_use_case = delete_attack_use_case
        
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.router.get(
            "/{attackId}",
            response_model=AttackDTO,
            responses={
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
