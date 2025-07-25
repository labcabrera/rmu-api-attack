"""
Attack web controller
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.infrastructure.dependency_container import container
from app.infrastructure.logging import log_endpoint, log_errors, get_logger
from app.infrastructure.adapters.web.attack_dtos import (
    AttackDTO,
    CreateAttackRequestDTO,
    AttackNotFoundDTO,
    PagedAttacksDTO,
)
from app.infrastructure.adapters.web.attack_dto_converter import (
    attack_to_dto,
    create_request_to_command,
    page_to_dto,
)

# Initialize logger for this module
logger = get_logger(__name__)

router = APIRouter(prefix="/attacks", tags=["Attacks"])


@router.get("", response_model=PagedAttacksDTO)
@log_endpoint
@log_errors
async def list_attacks(
    action_id: Optional[str] = Query(None, description="Filter by action ID"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    target_id: Optional[str] = Query(None, description="Filter by target ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(0, description="Page number (0-based)", ge=0),
    size: int = Query(100, description="Page size", ge=1, le=1000),
):
    """List attacks with optional filters"""
    logger.info(
        f"Listing attacks with filters - action_id: {action_id}, source_id: {source_id}, target_id: {target_id}, status: {status}, page: {page}, size: {size}"
    )

    try:
        list_use_case = container.get_list_attacks_use_case()
        result_page = await list_use_case.execute(
            action_id=action_id,
            source_id=source_id,
            target_id=target_id,
            status=status,
            page=page,
            size=size,
        )

        logger.info(
            f"Successfully retrieved page {result_page.pagination.page} with {len(result_page.content)} attacks (total: {result_page.pagination.total_elements})"
        )
        return page_to_dto(result_page)

    except Exception as e:
        logger.error(f"Error listing attacks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{attack_id}",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def get_attack(attack_id: str):
    """Get attack by ID"""
    logger.info(f"Retrieving attack with ID: {attack_id}")

    try:
        get_use_case = container.get_get_attack_use_case()
        attack = await get_use_case.execute(attack_id)

        if not attack:
            logger.warning(f"Attack not found: {attack_id}")
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id},
            )

        logger.info(f"Successfully retrieved attack: {attack_id}")
        return attack_to_dto(attack)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("", response_model=AttackDTO, status_code=201)
@log_endpoint
@log_errors
async def create_attack(request: CreateAttackRequestDTO):
    """Create a new attack"""
    logger.info(f"Creating new attack << actionId: {request.actionId}")

    try:
        create_use_case = container.get_create_attack_use_case()
        command = create_request_to_command(request)
        created_attack = await create_use_case.execute(command)
        logger.info(f"Successfully created attack: {created_attack.id}")
        return attack_to_dto(created_attack)

    except ValueError as e:
        logger.warning(f"Validation error creating attack: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating attack: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch(
    "/{attack_id}",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def update_attack(attack_id: str, update_data: dict):
    """Update attack (partial update)"""
    logger.info(f"Updating attack {attack_id} with data: {update_data}")

    try:
        update_use_case = container.get_update_attack_use_case()

        if not update_data:
            logger.warning(f"No update data provided for attack: {attack_id}")
            raise HTTPException(status_code=400, detail="No fields to update")

        attack = await update_use_case.execute(attack_id, update_data)

        if not attack:
            logger.warning(f"Attack not found for update: {attack_id}")
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id},
            )

        logger.info(f"Successfully updated attack: {attack_id}")
        return attack_to_dto(attack)

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error updating attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{attack_id}", status_code=204)
@log_endpoint
@log_errors
async def delete_attack(attack_id: str):
    """Delete attack by ID"""
    logger.info(f"Deleting attack: {attack_id}")

    try:
        delete_use_case = container.get_delete_attack_use_case()
        deleted = await delete_use_case.execute(attack_id)

        if not deleted:
            logger.warning(f"Attack not found for deletion: {attack_id}")
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id},
            )

        logger.info(f"Successfully deleted attack: {attack_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{attack_id}/roll",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def execute_attack_roll(attack_id: str, roll_data: dict):
    """Execute attack roll"""
    logger.info(f"Executing roll for attack {attack_id}: {roll_data}")

    try:
        roll_use_case = container.get_execute_attack_roll_use_case()
        roll_value = roll_data.get("roll")

        if roll_value is None:
            logger.warning(f"No roll value provided for attack: {attack_id}")
            raise HTTPException(status_code=400, detail="Roll value is required")

        attack = await roll_use_case.execute(attack_id, roll_value)

        if not attack:
            logger.warning(f"Attack not found for roll execution: {attack_id}")
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id},
            )

        logger.info(f"Successfully executed roll for attack {attack_id}: {roll_value}")
        return attack_to_dto(attack)

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            f"Validation error executing roll for attack {attack_id}: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing roll for attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{attack_id}/results",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def apply_attack_results(attack_id: str, results_data: dict):
    """Apply attack results"""
    logger.info(f"Applying results for attack {attack_id}: {results_data}")

    try:
        results_use_case = container.get_apply_attack_results_use_case()

        label = results_data.get("label")
        hit_points = results_data.get("hit_points", 0)
        criticals = results_data.get("criticals", [])

        if not label:
            logger.warning(f"No result label provided for attack: {attack_id}")
            raise HTTPException(status_code=400, detail="Result label is required")

        attack = await results_use_case.execute(attack_id, label, hit_points, criticals)

        if not attack:
            logger.warning(f"Attack not found for results application: {attack_id}")
            raise HTTPException(
                status_code=404,
                detail={"detail": "Attack not found", "attack_id": attack_id},
            )

        logger.info(f"Successfully applied results for attack {attack_id}")
        return attack_to_dto(attack)

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(
            f"Validation error applying results for attack {attack_id}: {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error applying results for attack {attack_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
