import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import pytest

from fastapi.testclient import TestClient
from app.main import app

# Initialize the lightweight synchronous execution client layer
client = TestClient(app)

@pytest.fixture
def unique_user_payload():
    """Generates an isolated, fresh mock account credentials payload."""
    import uuid
    random_id = uuid.uuid4().hex[:6]
    return {
        "email": f"test_doctor_{random_id}@hospital.org",
        "password": "SecurePassword123!",
        "full_name": f"Dr. Verification Unit {random_id}"
    }

def test_complete_platform_lifecycle_flow(unique_user_payload):
    """
    Executes an end-to-end integration test across all core services:
    Registration -> Authentication -> LangGraph Orchestration.
    """
    
    # 1. Verify User Profile Registration
    reg_response = client.post("/api/v1/auth/register", json=unique_user_payload)
    assert reg_response.status_code == 201, f"Registration failed: {reg_response.text}"
    assert reg_response.json()["email"] == unique_user_payload["email"]
    
    # 2. Verify Cryptographic JWT Issuance
    login_payload = {
        "username": unique_user_payload["email"],
        "password": unique_user_payload["password"]
    }
    login_response = client.post("/api/v1/auth/login", data=login_payload)
    assert login_response.status_code == 200, f"Authentication failed: {login_response.text}"
    
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Verify LangGraph Agentic Orchestration Routing
    agent_payload = {
        "session_id": "integration-test-session",
        "message": "Can you explain what a healthcare platform agent state pattern is?"
    }
    agent_response = client.post("/api/v1/agentic/agentic-execute", json=agent_payload, headers=auth_headers)
    assert agent_response.status_code == 200, f"Orchestrator failed: {agent_response.text}"
    
    graph_data = agent_response.json()
    assert "response" in graph_data
    assert "dispatched_path" in graph_data
    assert graph_data["dispatched_path"] == "general_chat"