# Minimal Task Management System – Django REST Backend

<p align="center">
  <img src="https://img.shields.io/badge/Version-v1.1-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-GPL%203.0-black?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/DB-PostgreSQL%20%7C%20SQLite-blue?style=for-the-badge" alt="Database">
  <img src="https://img.shields.io/badge/Tests-Passing-brightgreen?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/Features-Caching%2C%20Filtering%2C%20Pagination-brightgreen?style=for-the-badge" alt="Features">
</p>

---

A minimal Task Management API built with Django, Django REST Framework (DRF), and JWT authentication. Implements robust RBAC, custom User model, soft delete, filtering, pagination, caching, and core features as per assignment and beyond.

---

## Quickstart

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd <your-repo-dir>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Database

**PostgreSQL (recommended):**

Edit `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'taskdb',
        'USER': 'taskuser',
        'PASSWORD': 'taskpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Or SQLite for demo:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3. Migrate & Create Superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the server

```bash
python manage.py runserver
```

---

## Authentication Flow

- **Register:** `POST /auth/register/`
- **Login:** `POST /auth/login/` (returns JWT access/refresh)
- **Authenticated requests:** Set header `Authorization: Bearer <access_token>`
- **Refresh token:** `POST /auth/refresh/` with `refresh` token

---

## Core API Endpoints

### Auth

| Endpoint          | Method | Description     |
|-------------------|--------|----------------|
| /auth/register/   | POST   | Register user  |
| /auth/login/      | POST   | Login, get JWT |
| /auth/refresh/    | POST   | Refresh token  |

### Users (Admin only)

| Endpoint                    | Method | Description           |
|-----------------------------|--------|----------------------|
| /users/                     | GET    | List all users (filter & paginate) |
| /users/<id>/soft-delete/    | PATCH  | Soft-delete a user   |

### Tasks

| Endpoint           | Method   | Access   | Description                 |
|--------------------|----------|----------|-----------------------------|
| /tasks/            | GET      | Admin/User | List tasks (see only own as user; filter & paginate) |
| /tasks/            | POST     | Admin    | Create task                 |
| /tasks/<id>/       | GET      | Admin/User | Retrieve task (only assigned as user) |
| /tasks/<id>/       | PATCH    | Admin/User | Update task/Status (only own status as user) |
| /tasks/<id>/       | DELETE   | Admin    | Delete task                 |

### Comments

| Endpoint                       | Method | Access     | Description                         |
|---------------------------------|--------|------------|-------------------------------------|
| /tasks/<id>/comments/           | GET    | Admin/User | List comments (only own as user; filter & paginate) |
| /tasks/<id>/comments/           | POST   | User       | Add comment (only own tasks)        |

---

## Soft Delete Behavior

- Only admin can soft-delete users (`PATCH /users/<id>/soft-delete/`)
- Sets `is_active=False`
- Soft-deleted users CANNOT log in or access API
- Their tasks/comments remain (data preserved)
- They show as `is_active: false` in `/users/`
- Tasks show `assigned_to_inactive: true` if user is inactive

---

## RBAC Summary

- **Admin:**
    - Can create, update, delete any task
    - View all comments
    - Soft-delete users
- **User:**
    - Can view only own assigned tasks
    - Update only status of own tasks
    - Add comments only to own tasks
    - Cannot create or delete tasks

---

## Features

- **Robust RBAC** with custom DRF permissions.
- **Soft delete:** Data preserved, users deactivated.
- **JWT authentication** (`djangorestframework-simplejwt`).
- **Filtering** on tasks, users, comments (e.g. `/tasks/?status=Done`).
- **Pagination** on all list endpoints (see `results`, `count`, `next`, `previous` in response).
- **Caching** for main list endpoints (for efficiency).
- **Comprehensive tests:** See `test.py`.

---

## Running Tests

```bash
export API_URL=http://localhost:8000
python test.py
```

---

## API Docs

- See [`docs.md`](docs.md) for detailed API documentation, model structure, permissions, and design explanations.

---

## Contact

Reach out: [srujanparthasarathyiyengar@gmail.com](mailto:srujanparthasarathyiyengar@gmail.com)

<p align="center">
  <img src="https://img.shields.io/badge/Version-v1.1-blue?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/License-GPL%203.0-black?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/DB-PostgreSQL%20%7C%20SQLite-blue?style=for-the-badge" alt="Database">
  <img src="https://img.shields.io/badge/Tests-Passing-brightgreen?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/Features-Caching%2C%20Filtering%2C%20Pagination-brightgreen?style=for-the-badge" alt="Features">
</p>