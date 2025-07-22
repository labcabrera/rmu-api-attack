import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAttacksAPI:
    """Tests for the attacks endpoint"""
    
    def test_get_existing_attack(self):
        """Test to get an existing attack"""
        attack_id = "atk_001"
        response = client.get(f"/attacks/v1/{attack_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == attack_id
        assert data["tacticalGameId"] == "game_001"
        assert data["actionPoints"] == 3
        assert data["mode"] == "mainHand"
    
    def test_get_nonexistent_attack(self):
        """Test to get a non-existent attack"""
        attack_id = "atk_999"
        response = client.get(f"/attacks/v1/{attack_id}")
        
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"]["attack_id"] == attack_id
        assert data["detail"]["detail"] == "Attack not found"
    
    def test_get_attack_with_empty_id(self):
        """Test to validate that an empty ID cannot be used"""
        response = client.get("/attacks/v1/")
        
        # Should return 404 or 405 depending on FastAPI configuration
        assert response.status_code in [404, 405]
    
    def test_get_multiple_existing_attacks(self):
        """Test to verify that multiple different attacks can be obtained"""
        test_cases = [
            ("atk_001", "game_001", 3, "mainHand"),
            ("atk_002", "game_002", 4, "mainHand")
        ]

        for attack_id, expected_game_id, expected_action_points, expected_mode in test_cases:
            response = client.get(f"/attacks/v1/{attack_id}")
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == attack_id
            assert data["tacticalGameId"] == expected_game_id
            assert data["actionPoints"] == expected_action_points
            assert data["mode"] == expected_mode

class TestHealthEndpoints:
    """Tests for health and root endpoints"""
    
    def test_root_endpoint(self):
        """Test for the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "RMU API Attack" in data["message"]
    
    def test_health_check_endpoint(self):
        """Test for the health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
