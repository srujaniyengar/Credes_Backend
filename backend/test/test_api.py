import pytest
import requests
import uuid
import os
import jwt

API = os.environ.get("API_URL", "http://localhost:8000")

def unique_email():
    return f"user-{uuid.uuid4()}@example.com"

def user_id_from_token(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    return int(payload["user_id"])

@pytest.fixture
def user():
    email = unique_email()
    password = "TestPass123!"
    full_name = "Test User"
    r = requests.post(f"{API}/auth/register/", json={
        "email": email,
        "password": password,
        "full_name": full_name,
    })
    assert r.status_code in (200, 201)
    r = requests.post(f"{API}/auth/login/", json={
        "email": email,
        "password": password,
    })
    assert r.status_code == 200
    tokens = r.json()
    user_id = user_id_from_token(tokens["access"])
    return {
        "email": email,
        "password": password,
        "access": tokens["access"],
        "refresh": tokens["refresh"],
        "user_id": user_id,
    }

def test_create_and_update_task(user):
    headers = {"Authorization": f"Bearer {user['access']}"}
    # Create
    r = requests.post(f"{API}/tasks/", json={
        "title": "API Test Task",
        "description": "Pytest-created",
        "status": "To-Do",
        "assigned_to": user["user_id"],
    }, headers=headers)
    assert r.status_code in (200, 201)
    task = r.json()
    task_id = task["id"]
    assert task["assigned_to"] == user["user_id"]

    # Comment
    r = requests.post(f"{API}/tasks/{task_id}/comments/", json={
        "text": "Automated comment",
        "task": task_id,
        "author": user["user_id"]
    }, headers=headers)
    assert r.status_code in (200, 201)

    # Update
    r = requests.patch(f"{API}/tasks/{task_id}/", json={"title": "Pytest Updated"}, headers=headers)
    assert r.status_code == 200

    # Delete
    r = requests.delete(f"{API}/tasks/{task_id}/", headers=headers)
    assert r.status_code in (200, 204)

def test_bad_token(user):
    bad_headers = {"Authorization": "Bearer badtoken"}
    r = requests.get(f"{API}/tasks/", headers=bad_headers)
    assert r.status_code in (401, 403)

def test_missing_required_field(user):
    headers = {"Authorization": f"Bearer {user['access']}"}
    r = requests.post(f"{API}/tasks/", headers=headers, json={"description": "Missing title"})
    assert r.status_code in (400, 422)