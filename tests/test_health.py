import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "telephony_provider" in data
    assert "service" in data

def test_database_logging(client):
    from backend.services.db_service import db_service
    db_service.log_call("TEST_SID_123", "+919876543210")
    db_service.log_interaction("TEST_SID_123", "caller", "Hello test")
    calls = db_service.get_recent_calls(5)
    assert any(c["call_sid"] == "TEST_SID_123" for c in calls)
