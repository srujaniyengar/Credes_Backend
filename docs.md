<p align="center">
  <img src="https://img.shields.io/badge/Version-v1.0-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-GPL%203.0-black?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/DB-PostgreSQL%20%7C%20SQLite-blue?style=for-the-badge" alt="Database">
  <img src="https://img.shields.io/badge/Tests-Passing-brightgreen?style=for-the-badge" alt="Tests">
</p>

# Task Management API – Detailed Documentation (v1)

---

## 1. Custom User Model

**Approach**
- Subclassed `AbstractBaseUser` and `PermissionsMixin`.
- Email is the unique `USERNAME_FIELD`; no username.
- Fields: `email`, `full_name`, `role` (Admin/User), `date_joined`, `is_active`.
- Custom `UserManager` for user and superuser creation.

**Reasoning:**
- Email login is modern and required by the brief.
- `is_active` enables soft deletes and easy permission checks.

---

## 2. Authentication

- JWT (using `djangorestframework-simplejwt`) for stateless secure authentication.
- Custom JWT serializer denies login for inactive users.
- All protected endpoints require `Authorization: Bearer <access_token>`.

**Reasoning:**
- JWT is robust, stateless, and well supported in DRF.
- Secure: soft-deleted users can't auth or access any resources.

---

## 3. RBAC & Permissions

- Custom DRF permission classes:
    - `IsAdmin`: Admin-only endpoints.
    - `IsActiveUser`: Only for active users.
    - `IsAdminOrAssignedToForTask`: For task object-level access (admin or assigned user).
- Querysets and object permissions restrict access to only allowed resources and actions.

**Reasoning:**
- DRF permissions are declarative, reusable, and clear.
- All RBAC is enforced both at endpoint and object level for security.

---

## 4. Tasks & Comments

- **Task model:** title, description, status (`To-Do | In-Progress | Done`), `assigned_to` (FK), `created_at`, `updated_at`.
- **Comment model:** task (FK), author (FK), text, created_at.
- Admin can see all tasks and all comments.
- Users only see their own assigned tasks and comments on those tasks.

**Reasoning:**
- Model structure matches the brief and enables all required behaviors.
- Comments are always attached to a task and author.

---

## 5. Soft Delete

- **Endpoint:** `PATCH /users/<id>/soft-delete/` (admin only)
- Sets `is_active=False` on the user.
- User row is NOT deleted; all tasks and comments remain in the DB.
- Soft-deleted user cannot log in or access any endpoint (enforced via permissions and JWT).
- The `/users/` endpoint shows the user with `is_active: false`.
- The task serializer exposes `assigned_to_inactive: true` for tasks assigned to inactive users.

**Reasoning:**
- Preserves audit trail and business context.
- Cleanly disables a user and revokes all access with zero data loss.

---

## 6. API Endpoints – Details

### Auth

- **POST /auth/register/**  
  Register new user (anyone).
- **POST /auth/login/**  
  Login with email/password, returns JWT tokens.
- **POST /auth/refresh/**  
  Refresh JWT tokens.

### Users (Admin only)

- **GET /users/**  
  Admins list all users (shows all fields except password).
- **PATCH /users/<id>/soft-delete/**  
  Admin soft-deletes any user (not self).

### Tasks

- **GET /tasks/**
    - Admin: all tasks.
    - User: only own assigned tasks.
- **POST /tasks/**
    - Admin only: create a task and assign a user.
- **GET /tasks/<id>/**
    - Admin: any task.
    - User: only if assigned.
- **PATCH /tasks/<id>/**
    - Admin: update all fields.
    - User: can only PATCH `status` of assigned tasks.
- **DELETE /tasks/<id>/**
    - Admin only.

### Comments

- **GET /tasks/<id>/comments/**
    - Admin: all comments on any task.
    - User: comments only on their assigned tasks.
- **POST /tasks/<id>/comments/**
    - User: add comment only to own assigned tasks.

---

## 7. Example Flows

### Register
```http
POST /auth/register/
{
  "email": "user@example.com",
  "password": "testpass",
  "full_name": "Test User"
}
```

### Login
```http
POST /auth/login/
{
  "email": "user@example.com",
  "password": "testpass"
}
```
Response:
```json
{
  "refresh": "jwt-refresh-token...",
  "access": "jwt-access-token..."
}
```

### Soft Delete (as admin)
```http
PATCH /users/5/soft-delete/
Authorization: Bearer <ADMIN_TOKEN>
```
Response:
```json
{
  "id": 5,
  "email": "deleted@example.com",
  "is_active": false,
  ...
}
```

### User tries to login after soft delete
```http
POST /auth/login/
{
  "email": "deleted@example.com",
  "password": "testpass"
}
```
Response:
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

## 8. Testing

- The `test.py` script automates testing for:
    - Registration, login, RBAC enforcement
    - Admin/user flows for tasks and comments
    - Soft delete and inactive user access denial
    - Data integrity

---

## 9. Design Decisions

- **Soft delete** is enforced everywhere via `is_active` and DRF permissions.
- **RBAC** is separated into permission classes for clarity and reuse.
- **Data is never hard deleted** for audit, traceability, and integrity.
- **JWT** is used for stateless, scalable authentication.

---

## 10. FAQ

- **How do I enable optional features (filtering, pagination, docs)?**  
  These are reserved for v2 and will be described in a follow-up release.

---

## 11. Contact

Questions? [srujanparthasarathyiyengar@gmail.com](mailto:srujanparthasarathyiyengar@gmail.com)