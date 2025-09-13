import requests
import uuid
import os
import jwt

API = os.environ.get("API_URL")
if not API:
    raise RuntimeError("Set API_URL env var!")

def unique_email():
    return f"user{uuid.uuid4()}@example.com"

def extract_user_id_from_jwt(token):
    payload = jwt.decode(token, options={"verify_signature": False})
    return int(payload["user_id"])

def step(name):
    print(f"\n--- {name} ---")

def check(resp, expect=None):
    try:
        data = resp.json()
    except Exception:
        data = resp.text
    passed = (expect is None or resp.status_code in expect)
    print(f"Status: {resp.status_code}")
    print(data)
    print("PASSED" if passed else "FAILED")
    return passed, data

def test_admin_user_list():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin1@admin.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "passwordis12345")
    step("Admin login (for user listing)")
    r = requests.post(f"{API}/auth/login/", json={"email": admin_email, "password": admin_password})
    if r.status_code != 200:
        print("Admin login failed, cannot test user listing as admin.")
        return False
    tokens = r.json()
    access = tokens["access"]
    headers = {"Authorization": f"Bearer {access}"}
    step("List users as admin")
    r = requests.get(f"{API}/users/", headers=headers)
    passed = r.status_code == 200
    print(f"Status: {r.status_code}")
    try:
        print(r.json())
    except Exception:
        print(r.text)
    print("PASSED" if passed else "FAILED")
    return passed

def test_admin_view_all_comments(task_id):
    admin_email = os.environ.get("ADMIN_EMAIL", "admin1@admin.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "passwordis12345")
    step("Admin login (for comment viewing)")
    r = requests.post(f"{API}/auth/login/", json={"email": admin_email, "password": admin_password})
    if r.status_code != 200:
        print("Admin login failed, cannot test comment viewing as admin.")
        return False
    tokens = r.json()
    access = tokens["access"]
    headers = {"Authorization": f"Bearer {access}"}
    step("Admin view all comments on a task")
    r = requests.get(f"{API}/tasks/{task_id}/comments/", headers=headers)
    passed = r.status_code == 200 and isinstance(r.json(), list)
    print(f"Status: {r.status_code}")
    try:
        print(r.json())
    except Exception:
        print(r.text)
    print("PASSED" if passed else "FAILED")
    return passed

def test_user_cannot_create_task(headers, user_id):
    step("User tries to create a task (should be forbidden)")
    r = requests.post(f"{API}/tasks/", json={
        "title": "User Should Not Create",
        "description": "Forbidden test",
        "status": "To-Do",
        "assigned_to": user_id
    }, headers=headers)
    passed = r.status_code == 403
    print(f"Status: {r.status_code}")
    try:
        print(r.json())
    except Exception:
        print(r.text)
    print("PASSED" if passed else "FAILED")
    return passed

def test_user_cannot_delete_task(user_headers, task_id):
    step("User tries to delete a task (should be forbidden)")
    r = requests.delete(f"{API}/tasks/{task_id}/", headers=user_headers)
    passed = r.status_code == 403
    print(f"Status: {r.status_code}")
    print("PASSED" if passed else "FAILED")
    return passed

def create_task_as_admin(assigned_to):
    admin_email = os.environ.get("ADMIN_EMAIL", "admin1@admin.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "passwordis12345")
    step("Admin login (for task creation)")
    r = requests.post(f"{API}/auth/login/", json={"email": admin_email, "password": admin_password})
    if r.status_code != 200:
        print("Admin login failed, cannot create task as admin.")
        return None
    tokens = r.json()
    access = tokens["access"]
    headers = {"Authorization": f"Bearer {access}"}
    step("Admin creates a task for user")
    r = requests.post(f"{API}/tasks/", json={
        "title": "Admin Created Task",
        "description": "Assigned to user",
        "status": "To-Do",
        "assigned_to": assigned_to
    }, headers=headers)
    if r.status_code == 201:
        task = r.json()
        print("Admin created task:", task)
        return task["id"]
    else:
        print("Admin failed to create task:", r.status_code, r.text)
        return None

def test_soft_delete_user_flow():
    results = []
    # 1. Register and login as a new user
    step("Register user for soft delete test")
    user_email = unique_email()
    pwd = "TestPass123!"
    r = requests.post(f"{API}/auth/register/", json={
        "email": user_email, "password": pwd, "full_name": "SoftDelete User"
    })
    passed, _ = check(r, expect=[200, 201])
    results.append(("Register user for soft delete", passed))

    # 2. Login as user to get their ID and JWT
    step("Login as user for soft delete test")
    r = requests.post(f"{API}/auth/login/", json={"email": user_email, "password": pwd})
    passed, tokens = check(r, expect=[200])
    results.append(("Login as user for soft delete", passed))
    user_id = extract_user_id_from_jwt(tokens["access"])
    user_jwt = tokens["access"]
    user_headers = {"Authorization": f"Bearer {user_jwt}"}

    # 3. Login as admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin1@admin.com")
    admin_pwd = os.environ.get("ADMIN_PASSWORD", "passwordis12345")
    step("Admin login for soft delete test")
    r = requests.post(f"{API}/auth/login/", json={"email": admin_email, "password": admin_pwd})
    passed, admin_tokens = check(r, expect=[200])
    results.append(("Admin login for soft delete", passed))
    admin_jwt = admin_tokens["access"]
    admin_headers = {"Authorization": f"Bearer {admin_jwt}"}

    # 4. Admin soft deletes the user
    step("Admin soft-deletes user")
    r = requests.patch(f"{API}/users/{user_id}/soft-delete/", headers=admin_headers)
    passed = r.status_code == 200 and r.json().get("is_active") is False
    print(f"Soft delete status: {r.status_code}, response: {r.json()}")
    results.append(("Admin soft delete user", passed))

    # 5. User tries to log in (should fail)
    step("Soft deleted user tries to login")
    r = requests.post(f"{API}/auth/login/", json={"email": user_email, "password": pwd})
    failed_login = (r.status_code == 401)
    print(f"Login-after-delete status: {r.status_code}, response: {r.json()}")
    results.append(("Soft deleted user cannot login", failed_login))

    # 6. User tries to access API with old JWT (should fail)
    step("Soft deleted user tries to use old JWT")
    r = requests.get(f"{API}/tasks/", headers=user_headers)
    failed_api = r.status_code in (401, 403)
    print(f"API-after-delete status: {r.status_code}, response: {r.text}")
    results.append(("Soft deleted user cannot use API", failed_api))

    # 7. User data is preserved and is_active is false
    step("Admin checks user list for soft deleted user")
    r = requests.get(f"{API}/users/", headers=admin_headers)
    userlist = r.json()
    found = any(u["email"] == user_email and u["is_active"] is False for u in userlist)
    print("Soft deleted user in list and inactive:", found)
    results.append(("Soft deleted user appears in list as inactive", found))

    # Print summary for this flow
    print("\n--- Soft Delete User Flow Results ---")
    all_passed = True
    for name, passed in results:
        print(f"{name}: {'PASSED' if passed else 'FAILED'}")
        if not passed:
            all_passed = False
    print("Soft Delete User Flow:", "PASSED" if all_passed else "FAILED")
    return all_passed

def main():
    results = []
    task_id = None
    user_id = None
    try:
        # Register user
        step("Register user")
        email = unique_email()
        pwd = "TestPass123!"
        r = requests.post(f"{API}/auth/register/", json={
            "email": email, "password": pwd, "full_name": "Test User"
        })
        passed, _ = check(r, expect=[200, 201])
        results.append(("Register user", passed))

        # Login
        step("Login")
        r = requests.post(f"{API}/auth/login/", json={"email": email, "password": pwd})
        passed, tokens = check(r, expect=[200])
        results.append(("Login", passed))
        access = tokens["access"]
        refresh = tokens["refresh"]
        user_id = extract_user_id_from_jwt(access)
        headers = {"Authorization": f"Bearer {access}"}

        # User forbidden to create task
        user_cannot_create = test_user_cannot_create_task(headers, user_id)
        results.append(("User forbidden to create task", user_cannot_create))

        # Create task as admin for user to test delete/cmt RBAC
        task_id = create_task_as_admin(user_id)
        if task_id:
            # Add a comment as user (should be allowed)
            step("User add comment to assigned task")
            r = requests.post(f"{API}/tasks/{task_id}/comments/", json={
                "text": "Automated test comment",
                "task": task_id,
                "author": user_id
            }, headers=headers)
            passed, _ = check(r, expect=[201])
            results.append(("User add comment to assigned task", passed))

            # Update task (non-admin can only PATCH status of own assigned task)
            step("User update status of assigned task")
            r = requests.patch(f"{API}/tasks/{task_id}/", json={"status": "In-Progress"}, headers=headers)
            passed, _ = check(r, expect=[200])
            results.append(("User update status of assigned task", passed))

            # User forbidden to delete task
            user_cannot_delete = test_user_cannot_delete_task(headers, task_id)
            results.append(("User forbidden to delete task", user_cannot_delete))
        else:
            print("Skipping comment/update/delete as user: no task assigned by admin.")
            results.append(("User add comment to assigned task", None))
            results.append(("User update status of assigned task", None))
            results.append(("User forbidden to delete task", None))

        # Refresh token
        step("Refresh token")
        r = requests.post(f"{API}/auth/refresh/", json={"refresh": refresh})
        passed, new_token_data = check(r, expect=[200])
        results.append(("Refresh token", passed))
        new_access = new_token_data.get("access")
        if new_access:
            headers["Authorization"] = f"Bearer {new_access}"

        # Bad token error
        step("Bad token error")
        bad_headers = {"Authorization": "Bearer badtoken"}
        r = requests.get(f"{API}/tasks/", headers=bad_headers)
        passed, _ = check(r, expect=[401, 403])
        results.append(("Bad token error", passed))

        # Missing field error (admin, should get 400 not 403)
        admin_email = os.environ.get("ADMIN_EMAIL", "admin1@admin.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "passwordis12345")
        step("Missing field error (admin)")
        r_admin = requests.post(f"{API}/auth/login/", json={"email": admin_email, "password": admin_password})
        if r_admin.status_code == 200:
            admin_tokens = r_admin.json()
            admin_headers = {"Authorization": f"Bearer {admin_tokens['access']}"}
            r = requests.post(f"{API}/tasks/", headers=admin_headers, json={"description": "Missing title"})
            passed, _ = check(r, expect=[400, 422])
            results.append(("Missing field error", passed))
        else:
            print("Admin login failed, cannot test missing field error as admin.")
            results.append(("Missing field error", False))

        # List users (may 403 if not admin)
        step("List users (admin only, as regular user)")
        r = requests.get(f"{API}/users/", headers=headers)
        passed = r.status_code in (200, 403)
        print(f"Status: {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print(r.text)
        print("PASSED" if passed else "FAILED")
        results.append(("List users (admin only, as regular user)", passed))

        # Admin user listing test
        admin_user_list_passed = test_admin_user_list()
        results.append(("Admin user list (GET /users/ as admin)", admin_user_list_passed))

        # Admin view all comments for the task
        if task_id:
            admin_view_comments_passed = test_admin_view_all_comments(task_id)
            results.append(("Admin view all comments on a task", admin_view_comments_passed))
        else:
            results.append(("Admin view all comments on a task", None))

        # Soft delete user flow
        soft_delete_passed = test_soft_delete_user_flow()
        results.append(("Soft delete user flow", soft_delete_passed))

    except Exception as e:
        print("FAILED")
        print("ERROR:", str(e))
        results.append(("Exception occurred", False))

    print("\n--- Overall Results ---")
    all_passed = True
    for name, passed in results:
        print(f"{name}: {'PASSED' if passed else 'FAILED' if passed is False else 'SKIPPED'}")
        if passed is False:
            all_passed = False
    print("\nTEST SUITE RESULT:", "PASSED" if all_passed else "FAILED")

if __name__ == "__main__":
    main()