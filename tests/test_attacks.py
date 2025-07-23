import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.domain.entities.attack import Attack, AttackInput, AttackMode

# Mock attack data for testing
MOCK_ATTACK_DATA = {
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
        "roll": 15
    },
    "results": {
        "labelResult": "8AT",
        "hitPoints": 8,
        "criticals": [
            {
                "id": "crit_001",
                "status": "applied"
            }
        ]
    }
}

MOCK_ATTACK_DATA_2 = {
    "id": "atk_002",
    "tacticalGameId": "game_002",
    "status": "pending",
    "input": {
        "sourceId": "source_002",
        "targetId": "target_002",
        "actionPoints": 4,
        "mode": "offHand"
    },
    "roll": None,
    "results": None
}

client = TestClient(app)

class TestAttacksAPI:
    """Tests for the attacks endpoint"""
    
    @patch.object(attack_service, 'get_attack_by_id')
    def test_get_existing_attack(self, mock_get_attack):
        """Test to get an existing attack"""
        # Mock the service response
        mock_attack = Attack(**MOCK_ATTACK_DATA)
        mock_get_attack.return_value = mock_attack
        
        attack_id = "atk_001"
        response = client.get(f"/v1/attacks/{attack_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == attack_id
        assert data["tacticalGameId"] == "game_001"
        assert data["status"] == "executed"
        assert "input" in data
        assert data["input"]["sourceId"] == "source_001"
        assert data["input"]["targetId"] == "target_001"
        assert data["input"]["actionPoints"] == 3
        assert data["input"]["mode"] == "mainHand"
        assert "roll" in data
        assert data["roll"]["roll"] == 15
        assert "results" in data
        assert data["results"]["labelResult"] == "8AT"
        assert data["results"]["hitPoints"] == 8
        
        mock_get_attack.assert_called_once_with(attack_id)
    
    @patch.object(attack_service, 'get_attack_by_id')
    def test_get_nonexistent_attack(self, mock_get_attack):
        """Test to get a non-existent attack"""
        # Mock the service to return None
        mock_get_attack.return_value = None
        
        attack_id = "atk_999"
        response = client.get(f"/v1/attacks/{attack_id}")
        
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["attack_id"] == attack_id
        assert data["detail"]["detail"] == "Attack not found"
        
        mock_get_attack.assert_called_once_with(attack_id)
    
    @patch.object(attack_service, 'create_attack')
    def test_create_attack_success(self, mock_create_attack):
        """Test successful attack creation"""
        # Mock the service response
        mock_attack = Attack(**MOCK_ATTACK_DATA)
        mock_create_attack.return_value = mock_attack
        
        response = client.post("/v1/attacks/", json=MOCK_ATTACK_DATA)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "atk_001"
        assert data["tacticalGameId"] == "game_001"
        
        mock_create_attack.assert_called_once()
    
    @patch.object(attack_service, 'create_attack')
    def test_create_attack_duplicate(self, mock_create_attack):
        """Test attack creation with duplicate ID"""
        # Mock the service to raise ValueError
        mock_create_attack.side_effect = ValueError("Attack with ID atk_001 already exists")
        
        response = client.post("/v1/attacks/", json=MOCK_ATTACK_DATA)
        
        assert response.status_code == 409
        data = response.json()
        assert "Attack with ID atk_001 already exists" in data["detail"]
    
    @patch.object(attack_service, 'update_attack_partial')
    def test_patch_attack_success(self, mock_update_attack):
        """Test successful partial update of attack"""
        # Mock the service response
        updated_data = MOCK_ATTACK_DATA.copy()
        updated_data["status"] = "completed"
        mock_attack = Attack(**updated_data)
        mock_update_attack.return_value = mock_attack
        
        update_data = {"status": "completed"}
        response = client.patch("/v1/attacks/atk_001", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        
        mock_update_attack.assert_called_once_with("atk_001", update_data)
    
    @patch.object(attack_service, 'update_attack_partial')
    def test_patch_attack_not_found(self, mock_update_attack):
        """Test partial update of non-existent attack"""
        # Mock the service to return None
        mock_update_attack.return_value = None
        
        update_data = {"status": "completed"}
        response = client.patch("/v1/attacks/atk_999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["attack_id"] == "atk_999"
    
    @patch.object(attack_service, 'delete_attack')
    def test_delete_attack_success(self, mock_delete_attack):
        """Test successful attack deletion"""
        # Mock the service to return True
        mock_delete_attack.return_value = True
        
        response = client.delete("/v1/attacks/atk_001")
        
        assert response.status_code == 204
        
        mock_delete_attack.assert_called_once_with("atk_001")
    
    @patch.object(attack_service, 'delete_attack')
    def test_delete_attack_not_found(self, mock_delete_attack):
        """Test deletion of non-existent attack"""
        # Mock the service to return False
        mock_delete_attack.return_value = False
        
        response = client.delete("/v1/attacks/atk_999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["attack_id"] == "atk_999"
    
    @patch.object(attack_service, 'list_attacks')
    def test_list_attacks_success(self, mock_list_attacks):
        """Test successful listing of attacks"""
        # Mock the service response
        mock_attacks = [
            Attack(**MOCK_ATTACK_DATA),
            Attack(**MOCK_ATTACK_DATA_2)
        ]
        mock_list_attacks.return_value = mock_attacks
        
        response = client.get("/v1/attacks/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "atk_001"
        assert data[1]["id"] == "atk_002"
        
        mock_list_attacks.assert_called_once_with(
            tactical_game_id=None,
            status=None,
            limit=100,
            skip=0
        )
    
    @patch.object(attack_service, 'list_attacks')
    def test_list_attacks_with_filters(self, mock_list_attacks):
        """Test listing attacks with filters"""
        # Mock the service response
        mock_attacks = [Attack(**MOCK_ATTACK_DATA)]
        mock_list_attacks.return_value = mock_attacks
        
        response = client.get("/v1/attacks/?tactical_game_id=game_001&status=executed&limit=10&skip=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        mock_list_attacks.assert_called_once_with(
            tactical_game_id="game_001",
            status="executed",
            limit=10,
            skip=5
        )

class TestHealthEndpoints:
    """Tests for health and root endpoints"""
    
    def test_root_endpoint(self):
        """Test for the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "RMU API Attack" in data["message"]
        assert "version" in data
        assert "api_prefix" in data
    
    @patch.object(attack_service, 'connect')
    def test_health_check_endpoint_success(self, mock_connect):
        """Test for the health check endpoint with successful DB connection"""
        # Mock successful connection
        mock_connect.return_value = None
        
        response = client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["database"] == "connected"
        assert "mongodb_url" in data
    
    @patch.object(attack_service, 'connect')
    def test_health_check_endpoint_db_error(self, mock_connect):
        """Test for the health check endpoint with DB connection error"""
        # Mock connection error
        mock_connect.side_effect = Exception("Connection failed")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error: Connection failed" in data["database"]
