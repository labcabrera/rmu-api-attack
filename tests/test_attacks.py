from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.domain.exceptions import AttackNotFoundException
from app.domain.entities import (
    Attack,
    AttackArmor,
    AttackModifiers,
    AttackRollModifiers,
    AttackSituationalModifiers,
)
from app.domain.entities.enums import AttackStatus, AttackType
from app.interfaces.http.attack_controller import search_attack_by_id
from app.interfaces.http.dto import CreateAttackRequestDTO
from app.main import app, root


def build_attack() -> Attack:
    return Attack(
        id="atk_001",
        game_id="game_001",
        action_id="action_001",
        source_id="source_001",
        target_id="target_001",
        status=AttackStatus.APPLIED,
        modifiers=AttackModifiers(
            attack_type=AttackType.MELEE,
            attack_table="arming-sword",
            attack_size=2,
            fumble_table="melee-one-hand",
            armor=AttackArmor(at=1),
            roll_modifiers=AttackRollModifiers(bo=85, bd=25),
            situational_modifiers=AttackSituationalModifiers(
                source_status=[],
                target_status=[],
            ),
            features=[],
            source_skills=[],
        ),
    )


@pytest.mark.asyncio
async def test_root_handler():
    response = await root()

    assert response["message"].startswith("RMU API Attack")
    assert response["api_prefix"] == "/v1"


def test_attacks_routes_use_current_v1_prefix():
    route_paths = {route.path for route in app.routes}

    assert "/v1/attacks" in route_paths
    assert "/v1/attacks/{attack_id}" in route_paths
    assert "/api/v1/attacks" not in route_paths


def test_create_attack_request_rejects_invalid_payload():
    with pytest.raises(ValidationError):
        CreateAttackRequestDTO.model_validate({})


@pytest.mark.asyncio
async def test_search_attack_by_id_handler_returns_current_dto():
    use_case = AsyncMock()
    use_case.execute.return_value = build_attack()

    with patch(
        "app.interfaces.http.attack_controller.container.search_attack_by_id_use_case",
        return_value=use_case,
    ):
        response = await search_attack_by_id("atk_001")

    assert response.id == "atk_001"
    assert response.gameId == "game_001"
    assert response.actionId == "action_001"
    assert response.status == "applied"
    use_case.execute.assert_awaited_once_with("atk_001")


@pytest.mark.asyncio
async def test_search_attack_by_id_handler_maps_not_found_to_404():
    use_case = AsyncMock()
    use_case.execute.side_effect = AttackNotFoundException("missing")

    with patch(
        "app.interfaces.http.attack_controller.container.search_attack_by_id_use_case",
        return_value=use_case,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await search_attack_by_id("missing")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["attack_id"] == "missing"
