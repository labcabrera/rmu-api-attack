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
            ("atk_001", "game_001", "executed", "source_001", "target_001"),
            ("atk_002", "game_002", "pending", "source_002", "target_002")
        ]

        for attack_id, expected_game_id, expected_status, expected_source, expected_target in test_cases:
            response = client.get(f"/attacks/v1/{attack_id}")
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["id"] == attack_id
            assert data["tacticalGameId"] == expected_game_id
            assert data["status"] == expected_status
            assert data["input"]["sourceId"] == expected_source
            assert data["input"]["targetId"] == expected_target

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
