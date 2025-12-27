from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_topic():
    response = client.post(
        "topics",
        json={"name": "Test Topic"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Topic created successfully"}

    response = client.get("topics")
    assert response.status_code == 200

    topics = response.json()
    found = any(t["name"] == "Test Topic" for t in topics)
    assert found

def test_login_failure():
    response = client.post(
        "login",
        json={"username": "fakeuser", "password": "wrongpassword"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User not found"}