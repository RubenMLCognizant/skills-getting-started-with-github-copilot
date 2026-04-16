import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # TestClient follows redirects by default
    # Could check content, but for now just status

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success():
    # Assuming "Chess Club" has participants, add a new one
    initial_count = len(client.get("/activities").json()["Chess Club"]["participants"])
    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Check added
    updated = client.get("/activities").json()["Chess Club"]["participants"]
    assert len(updated) == initial_count + 1
    assert "newstudent@mergington.edu" in updated

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Tennis Club/signup", params={"email": "test@mergington.edu"})
    # Try again
    response = client.post("/activities/Tennis Club/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Art Club/signup", params={"email": "removeme@mergington.edu"})
    initial_count = len(client.get("/activities").json()["Art Club"]["participants"])
    response = client.delete("/activities/Art Club/signup", params={"email": "removeme@mergington.edu"})
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    updated = client.get("/activities").json()["Art Club"]["participants"]
    assert len(updated) == initial_count - 1
    assert "removeme@mergington.edu" not in updated

def test_unregister_activity_not_found():
    response = client.delete("/activities/NonExistent/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Debate Team/signup", params={"email": "notsigned@mergington.edu"})
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]