from unittest.mock import MagicMock, patch
from main import app

def override_consumer_auth():
    return MagicMock(user_id=20, role="consumer")

def test_register_consumer(client):
    """Test consumer registration."""
    with patch("routers.consumers.create_consumer") as mock_create:
        mock_create.return_value = True
        
        payload = {
            "email": "consumer@test.com",
            "password": "securepass",
            "first_name": "Furkan",
            "last_name": "RuggedHill"
        }
        
        response = client.post("/consumers", json=payload)
        
        assert response.status_code == 201
        mock_create.assert_called_once()

@patch("routers.consumers.ReservationsQuerier")
def test_get_my_reservations(MockQuerier, client):
    app.dependency_overrides["internal.auth.middleware.consumer_auth"] = override_consumer_auth
    
    mock_res = MagicMock(reservation_id=101, bundle_id=5)
    MockQuerier.return_value.get_consumers_reservations.return_value = [mock_res]

    response = client.get("/consumers/me/reservations")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["reservation_id"] == 101
    
    del app.dependency_overrides["internal.auth.middleware.consumer_auth"]

@patch("routers.consumers.ReservationsQuerier")
def test_get_my_reservations_empty(MockQuerier, client):
    """Test 500 error when no reservations found (per implementation)."""
    app.dependency_overrides["internal.auth.middleware.consumer_auth"] = override_consumer_auth
    
    MockQuerier.return_value.get_consumers_reservations.return_value = []

    response = client.get("/consumers/me/reservations")

    assert response.status_code == 500
    assert "failed to get reservations" in response.json()["detail"]
    
    del app.dependency_overrides["internal.auth.middleware.consumer_auth"]

@patch("routers.consumers.ConsumerQuerier")
def test_update_consumer(MockQuerier, client):
    app.dependency_overrides["internal.auth.middleware.consumer_auth"] = override_consumer_auth
    
    MockQuerier.return_value.update_consumer.return_value = True

    payload = {
        "first_name": "Who",
        "last_name": "should it be"
    }

    response = client.patch("/consumers/me", json=payload)

    assert response.status_code == 200
    assert response.text == '"consumer was updated"'
    
    del app.dependency_overrides["internal.auth.middleware.consumer_auth"]

@patch("routers.consumers.ConsumerQuerier")
def test_update_consumer_fail(MockQuerier, client):
    app.dependency_overrides["internal.auth.middleware.consumer_auth"] = override_consumer_auth
    
    MockQuerier.return_value.update_consumer.return_value = None

    payload = {"first_name": "X", "last_name": "Y"}
    
    response = client.patch("/consumers/me", json=payload)

    assert response.status_code == 500
    
    del app.dependency_overrides["internal.auth.middleware.consumer_auth"]