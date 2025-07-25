"""
Attack web controller.
"""

from typing import Optional
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

logger = get_logger(__name__)

router = APIRouter(prefix="/attacks", tags=["Attacks"])


@router.get(
    "",
    summary="Search attacks by RSQL",
    description="Search attacks using RSQL query language.",
    response_model=PagedAttacksDTO,
)
@log_endpoint
@log_errors
async def search_attacks_by_rsql(
    search: Optional[str] = Query(
        "",
        description="RSQL query string for filtering (e.g., 'status==draft;actionId==action_001')",
    ),
    page: int = Query(0, description="Page number (0-based)", ge=0),
    size: int = Query(10, description="Page size", ge=1),
):

    logger.info(f"Search attacks << search: {search}, page: {page}, size: {size}")
    try:
        use_case = container.get_search_attack_by_rsql_use_case()
        result_page = await use_case.execute(
            rsql_query=search,
            page=page,
            size=size,
        )
        return page_to_dto(result_page)
    except Exception as e:
        logger.error(f"Error listing attacks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{attack_id}",
    summary="Get attack by Id",
    description="Retrieve an attack by its unique identifier.",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def search_attack_by_id(attack_id: str):
    """Get attack by ID"""
    logger.info(f"Retrieving attack with ID: {attack_id}")

    try:
        use_case = container.get_search_attack_by_id_use_case()
        attack = await use_case.execute(attack_id)

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


@router.post(
    "",
    summary="Create a new attack",
    description="Create a new attack with the provided details.",
    response_model=AttackDTO,
    status_code=201,
)
@log_endpoint
@log_errors
async def create_attack(request: CreateAttackRequestDTO):
    """Create a new attack"""
    logger.info(f"Creating new attack << actionId: {request.actionId}")

    try:
        command = create_request_to_command(request)
        use_case = container.get_create_attack_use_case()
        created_attack = await use_case.execute(command)
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
    summary="Update attack modifiers",
    description="Update an existing attack with the provided information.",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def update_attack(attack_id: str, update_data: dict):
    """Update attack (partial update)"""
    logger.info(f"Updating attack {attack_id} with data: {update_data}")

    try:
        if not update_data:
            logger.warning(f"No update data provided for attack: {attack_id}")
            raise HTTPException(status_code=400, detail="No fields to update")
        use_case = container.get_update_attack_modifiers_use_case()
        attack = await use_case.execute(attack_id, update_data)

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


@router.delete(
    "/{attack_id}",
    summary="Delete attack by ID",
    description="Delete an existing attack by its unique identifier.",
    status_code=204,
)
@log_endpoint
@log_errors
async def delete_attack(attack_id: str):
    """Delete attack by ID"""
    logger.info(f"Deleting attack: {attack_id}")

    try:
        use_case = container.get_delete_attack_use_case()
        deleted = await use_case.execute(attack_id)
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
    summary="Apply attack roll",
    description="Applies the result of the damage roll to an attack.",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def execute_attack_roll(attack_id: str, roll_data: dict):
    """Applies the result of the damage roll to an attack."""
    logger.info(f"Executing roll for attack {attack_id}: {roll_data}")

    try:
        roll_value = roll_data.get("roll")
        if roll_value is None:
            logger.warning(f"No roll value provided for attack: {attack_id}")
            raise HTTPException(status_code=400, detail="Roll value is required")
        use_case = container.get_update_attack_roll_use_case()
        attack = await use_case.execute(attack_id, roll_value)
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
    "/{attack_id}/apply",
    summary="Apply attack result",
    description="Apply the result of the attack to the tactical module.",
    response_model=AttackDTO,
    responses={404: {"model": AttackNotFoundDTO}},
)
@log_endpoint
@log_errors
async def apply_attack_results(attack_id: str, results_data: dict):
    """Apply attack results."""
    logger.info(f"Applying results for attack {attack_id}: {results_data}")

    try:
        use_case = container.get_apply_attack_use_case()
        attack = await use_case.execute(attack_id, results_data)
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
