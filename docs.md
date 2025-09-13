# Task Management API – Detailed Documentation (v1.1)

---

## 1. Custom User Model

- Subclassed `AbstractBaseUser` and `PermissionsMixin`.
- Email is the unique `USERNAME_FIELD`; no username.
- Fields: `email`, `full_name`, `role` (`Admin`/`User`), `date_joined`, `is_active`.
- Custom `UserManager` for user and superuser creation.
- **Soft delete** is implemented by setting `is_active=False`.

---

## 2. Authentication

- JWT (using `djangorestframework-simplejwt`) for stateless secure authentication.
- Custom JWT serializer denies login for inactive users.
- All protected endpoints require `Authorization: Bearer <access_token>`.

---

## 3. RBAC & Permissions

- Custom DRF permission classes:
    - `IsAdmin`: Admin-only endpoints.
    - `IsActiveUser`: Only for active users.
    - `IsAdminOrAssignedToForTask`: For task object-level access (admin or assigned user).
- Querysets and object permissions restrict access to only allowed resources and actions.

---

## 4. Tasks & Comments

- **Task model:** `title`, `description`, `status` (`To-Do` | `In-Progress` | `Done`), `assigned_to` (FK), `created_at`, `updated_at`.
- **Comment model:** `task` (FK), `author` (FK), `text`, `created_at`.
- Admin can see all tasks and all comments.
- Users only see their own assigned tasks and comments on those tasks.

---

## 5. Soft Delete

- **Endpoint:** `PATCH /users/<id>/soft-delete/` (admin only)
- Sets `is_active=False` on the user.
- User row is NOT deleted; all tasks and comments remain.
- Soft-deleted user cannot log in or access any endpoint (enforced via permissions and JWT).
- `/users/` endpoint shows the user with `is_active: false`.
- Task serializer exposes `assigned_to_inactive: true` for tasks assigned to inactive users.

---

## 6. Caching, Filtering & Pagination

- **Caching:** List endpoints (`/tasks/`, `/users/`, `/tasks/<id>/comments/`) are cached (5 minutes).
- **Filtering:** All list endpoints support query param filters, e.g.:
    - `/tasks/?status=Done`
    - `/users/?role=User&is_active=true`
    - `/tasks/<id>/comments/?author=<user_id>`
- **Pagination:** All list endpoints use DRF's pagination:
    - Response includes `count`, `next`, `previous`, `results`.

---

## 7. API Endpoints – Details

### Auth

- **POST /auth/register/**  
  Register new user (anyone).
- **POST /auth/login/**  
  Login with email/password, returns JWT tokens.
- **POST /auth/refresh/**  
  Refresh JWT tokens.

### Users (Admin only)

- **GET /users/**  
  Admins list all users (supports filters/pagination).
- **PATCH /users/<id>/soft-delete/**  
  Admin soft-deletes any user (not self).

### Tasks

- **GET /tasks/**
    - Admin: all tasks.
    - User: only own assigned tasks.
    - Supports filters/pagination.
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
    - Supports filters/pagination.
- **POST /tasks/<id>/comments/**
    - User: add comment only to own assigned tasks.

---

## 8. Example Flows

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

### List Tasks (with Filtering & Pagination)
```http
GET /tasks/?status=To-Do&page=1&page_size=5
Authorization: Bearer <TOKEN>
```
Response:
```json
{
  "count": 11,
  "next": "http://localhost:8000/tasks/?status=To-Do&page=2&page_size=5",
  "previous": null,
  "results": [
    {
      "id": 3,
      "title": "Some Task",
      "description": "...",
      "status": "To-Do",
      "assigned_to": 4,
      "assigned_to_inactive": false,
      ...
    },
    ...
  ]
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

## 9. Testing

- The `test.py` script automates testing for:
    - Registration, login, RBAC enforcement
    - Admin/user flows for tasks and comments
    - Soft delete and inactive user access denial
    - Filtering, pagination, and data integrity

---

## 10. Design Decisions

- **Soft delete** is enforced everywhere via `is_active` and DRF permissions.
- **RBAC** is separated into permission classes for clarity and reuse.
- **Data is never hard deleted** for audit, traceability, and integrity.
- **JWT** is used for stateless, scalable authentication.
- **Filtering, pagination, and caching** are implemented for practical, real-world usability.

---

## 11. FAQ

- **How do I enable optional features (filtering, pagination, docs)?**  
  These are now enabled in v1.1. See examples above.

---

## 12. Contact

Questions? [srujanparthasarathyiyengar@gmail.com](mailto:srujanparthasarathyiyengar@gmail.com)