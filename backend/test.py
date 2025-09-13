import requests
import random
import string

API = "http://localhost:8000"

def random_email():
    return "user{}@example.com".format(''.join(random.choices(string.digits, k=6)))

def print_header(msg):
    print("\n" + "="*len(msg))
    print(msg)
    print("="*len(msg))

def check(resp):
    print(f"Status: {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)
    print()

def main():
    # 1. Register a new user
    print_header("1. Register new user")
    email = random_email()
    password = "TestPass123!"
    user_data = {
        "email": email,
        "password": password,
        "full_name": "Test User"
    }
    r = requests.post(f"{API}/auth/register/", json=user_data)
    check(r)
    assert r.status_code in [200, 201], "Registration failed"

    # 2. Log in to get tokens
    print_header("2. Login")
    r = requests.post(f"{API}/auth/login/", json=user_data)
    check(r)
    tokens = r.json()
    access = tokens["access"]
    refresh = tokens["refresh"]
    headers = {"Authorization": f"Bearer {access}"}
    user_id = None  # We'll get it from task creation

    # 3. Create a task
    print_header("3. Create a task")
    task_data = {
        "title": "API Test Task",
        "description": "Created by automated test script",
        "status": "To-Do"
        # 'assigned_to' left out intentionally if your API assigns to self by default;
        # otherwise, you can try 'assigned_to': 1 or whichever user id is valid.
    }
    r = requests.post(f"{API}/tasks/", json=task_data, headers=headers)
    check(r)
    assert r.status_code in [200, 201], "Task creation failed"
    task = r.json()
    task_id = task["id"]
    user_id = task.get("assigned_to", 1)  # fallback to 1 if not present

    # 4. List all tasks
    print_header("4. List all tasks")
    r = requests.get(f"{API}/tasks/", headers=headers)
    check(r)
    assert r.status_code == 200, "Task list failed"

    # 5. Add a comment to the task (with explicit 'task' and 'author')
    print_header("5. Add a comment to task")
    comment_data = {
        "text": "Automated test comment",
        "task": task_id,
        "author": user_id
    }
    r = requests.post(f"{API}/tasks/{task_id}/comments/", json=comment_data, headers=headers)
    check(r)
    assert r.status_code in [200, 201], "Adding comment failed"

    # 6. Update the task
    print_header("6. Update the task")
    r = requests.patch(f"{API}/tasks/{task_id}/", json={"title": "Updated by test.py"}, headers=headers)
    check(r)
    assert r.status_code == 200, "Task update failed"

    # 7. Refresh token
    print_header("7. Refresh token")
    r = requests.post(f"{API}/auth/refresh/", json={"refresh": refresh})
    check(r)
    new_access = r.json().get("access")
    if new_access:
        headers["Authorization"] = f"Bearer {new_access}"

    # 8. Error handling: Bad token
    print_header("8. Error: Bad token")
    bad_headers = {"Authorization": "Bearer badtoken"}
    r = requests.get(f"{API}/tasks/", headers=bad_headers)
    check(r)

    # 9. Error handling: Missing field
    print_header("9. Error: Missing required field")
    r = requests.post(f"{API}/tasks/", headers=headers, json={"description": "Missing title"})
    check(r)

    # 10. List users (may be forbidden if not admin)
    print_header("10. List users (admin only)")
    r = requests.get(f"{API}/users/", headers=headers)
    check(r)

    # 11. Delete the created task
    print_header("11. Delete the task")
    r = requests.delete(f"{API}/tasks/{task_id}/", headers=headers)
    print(f"Status: {r.status_code}")
    print(r.text)

if __name__ == "__main__":
    main()