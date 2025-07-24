import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.domain.entities import (
    Attack,
    AttackModifiers,
    AttackMode,
    AttackRoll,
    AttackResult,
)
from app.infrastructure.dependency_container import container

# Mock attack data for testing
MOCK_ATTACK_1 = Attack(
    id="atk_001",
    tactical_game_id="game_001",
    status="executed",
    input=AttackModifiers(
        source_id="source_001",
        target_id="target_001",
        action_points=3,
        mode=AttackMode.MAIN_HAND,
        round=1,
    ),
    roll=AttackRoll(roll=15),
    results=None,
)

MOCK_ATTACK_2 = Attack(
    id="atk_002",
    tactical_game_id="game_001",
    status="pending",
    input=AttackModifiers(
        source_id="source_002",
        target_id="target_002",
        action_points=4,
        mode=AttackMode.OFF_HAND,
        round=1,
    ),
    roll=None,
    results=None,
)

client = TestClient(app)


class TestAttacksAPI:
    """Tests for the attacks endpoint"""

    @patch.object(container, "get_get_attack_use_case")
    def test_get_existing_attack(self, mock_get_use_case):
        """Test to get an existing attack"""
        # Mock the use case and its execute method
        mock_use_case = AsyncMock()
        mock_attack = Attack(
            id="atk_001",
            tactical_game_id="game_001",
            status="executed",
            input=AttackModifiers(
                source_id="source_001",
                target_id="target_001",
                action_points=3,
                mode=AttackMode.MAIN_HAND,
                round=1,
            ),
            roll=AttackRoll(roll=15),
            results=None,
        )
        mock_use_case.execute.return_value = mock_attack
        mock_get_use_case.return_value = mock_use_case

        attack_id = "atk_001"

        response = client.get(f"/api/v1/attacks/{attack_id}")

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == attack_id
        assert data["tacticalGameId"] == "game_001"
        assert data["status"] == "executed"
        assert data["input"]["sourceId"] == "source_001"
        assert data["input"]["targetId"] == "target_001"
        assert data["input"]["actionPoints"] == 3
        assert data["input"]["mode"] == "mainHand"
        assert "roll" in data
        assert data["roll"]["roll"] == 15

        mock_use_case.execute.assert_called_once_with(attack_id)

    @patch.object(container, "get_get_attack_use_case")
    def test_get_nonexistent_attack(self, mock_get_use_case):
        """Test to get a non-existent attack"""
        # Mock the use case to return None
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None
        mock_get_use_case.return_value = mock_use_case

        attack_id = "non_existent"

        response = client.get(f"/api/v1/attacks/{attack_id}")

        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

        mock_use_case.execute.assert_called_once_with(attack_id)

    @patch.object(container, "get_create_attack_use_case")
    def test_create_attack_success(self, mock_create_use_case):
        """Test successful attack creation"""
        # Mock the use case and its execute method
        mock_use_case = AsyncMock()
        mock_attack = Attack(
            id="atk_001",
            tactical_game_id="game_001",
            status="executed",
            input=AttackModifiers(
                source_id="source_001",
                target_id="target_001",
                action_points=3,
                mode=AttackMode.MAIN_HAND,
                round=1,
            ),
            roll=AttackRoll(roll=15),
            results=None,
        )
        mock_use_case.execute.return_value = mock_attack
        mock_create_use_case.return_value = mock_use_case

        attack_data = {
            "tacticalGameId": "game_001",
            "sourceId": "source_001",
            "targetId": "target_001",
            "actionPoints": 3,
            "mode": "mainHand",
            "round": 1,
        }

        response = client.post("/api/v1/attacks", json=attack_data)

        assert response.status_code == 201
        mock_use_case.execute.assert_called_once()

    def test_create_attack_invalid_data(self):
        """Test attack creation with invalid data"""
        invalid_data = {
            "tacticalGameId": "",  # Invalid empty string
            "input": {
                "sourceId": "source_001",
                "actionPoints": -1,  # Invalid negative value
                "mode": "invalidMode",  # Invalid mode
            },
        }

        response = client.post("/api/v1/attacks", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @patch.object(container, "get_update_attack_use_case")
    def test_update_attack_success(self, mock_update_use_case):
        """Test successful attack update"""
        # Mock the use case
        mock_use_case = AsyncMock()
        mock_attack = MOCK_ATTACK_1
        mock_use_case.execute.return_value = mock_attack
        mock_update_use_case.return_value = mock_use_case

        attack_id = "atk_001"
        update_data = {"status": "completed"}

        response = client.patch(f"/api/v1/attacks/{attack_id}", json=update_data)

        assert response.status_code == 200
        mock_use_case.execute.assert_called_once()

    @patch.object(container, "get_update_attack_use_case")
    def test_update_nonexistent_attack(self, mock_update_use_case):
        """Test update of non-existent attack"""
        # Mock the use case to return None
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None
        mock_update_use_case.return_value = mock_use_case

        attack_id = "non_existent"
        update_data = {"status": "completed"}

        response = client.patch(f"/api/v1/attacks/{attack_id}", json=update_data)

        assert response.status_code == 404

    @patch.object(container, "get_delete_attack_use_case")
    def test_delete_attack_success(self, mock_delete_use_case):
        """Test successful attack deletion"""
        # Mock the use case
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = True
        mock_delete_use_case.return_value = mock_use_case

        attack_id = "atk_001"

        response = client.delete(f"/api/v1/attacks/{attack_id}")

        assert response.status_code == 204

    @patch.object(container, "get_delete_attack_use_case")
    def test_delete_nonexistent_attack(self, mock_delete_use_case):
        """Test deletion of non-existent attack"""
        # Mock the use case to return False
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = False
        mock_delete_use_case.return_value = mock_use_case

        attack_id = "non_existent"

        response = client.delete(f"/api/v1/attacks/{attack_id}")

        assert response.status_code == 404

    @patch.object(container, "get_list_attacks_use_case")
    def test_list_attacks_success(self, mock_list_use_case):
        """Test successful attacks listing"""
        # Mock the use case
        mock_use_case = AsyncMock()
        mock_attacks = [MOCK_ATTACK_1, MOCK_ATTACK_2]
        mock_use_case.execute.return_value = mock_attacks
        mock_list_use_case.return_value = mock_use_case

        response = client.get("/api/v1/attacks")

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "atk_001"
        assert data[1]["id"] == "atk_002"

    @patch.object(container, "get_list_attacks_use_case")
    def test_list_attacks_with_filters(self, mock_list_use_case):
        """Test attacks listing with filters"""
        # Mock the use case
        mock_use_case = AsyncMock()
        mock_attacks = [MOCK_ATTACK_1]
        mock_use_case.execute.return_value = mock_attacks
        mock_list_use_case.return_value = mock_use_case

        params = {
            "tactical_game_id": "game_001",
            "status": "executed",
            "limit": 10,
            "skip": 0,
        }

        response = client.get("/api/v1/attacks", params=params)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "atk_001"

    @patch.object(container, "get_execute_attack_roll_use_case")
    def test_execute_attack_roll_success(self, mock_roll_use_case):
        """Test successful attack roll execution"""
        # Mock the use case
        mock_use_case = AsyncMock()
        # Create updated attack with new roll value
        updated_attack = Attack(
            id="atk_001",
            tactical_game_id="game_001",
            status="executed",
            input=AttackModifiers(
                source_id="source_001",
                target_id="target_001",
                action_points=3,
                mode=AttackMode.MAIN_HAND,
                round=1,
            ),
            roll=AttackRoll(roll=18),
            results=None,
        )
        mock_use_case.execute.return_value = updated_attack
        mock_roll_use_case.return_value = mock_use_case

        attack_id = "atk_001"
        roll_data = {"roll": 18}

        response = client.post(f"/api/v1/attacks/{attack_id}/roll", json=roll_data)

        assert response.status_code == 200

        data = response.json()
        assert data["roll"]["roll"] == 18

    @patch.object(container, "get_execute_attack_roll_use_case")
    def test_execute_attack_roll_not_found(self, mock_roll_use_case):
        """Test attack roll execution for non-existent attack"""
        # Mock the use case to return None
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = None
        mock_roll_use_case.return_value = mock_use_case

        attack_id = "non_existent"
        roll_data = {"roll": 15}

        response = client.post(f"/api/v1/attacks/{attack_id}/roll", json=roll_data)

        assert response.status_code == 404


class TestHealthEndpoints:
    """Tests for health and root endpoints"""

    def test_root_endpoint(self):
        """Test for the root endpoint"""
        response = client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "RMU API Attack" in data["message"]
