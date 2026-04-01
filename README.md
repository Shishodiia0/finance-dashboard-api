# Finance Dashboard API

A backend API for a finance dashboard system with role-based access control, financial record management, and summary analytics.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + bcrypt |

---

## Project Structure

```
src/
  api/routes/       → auth, users, records, dashboard
  core/             → config, security, dependencies (guards)
  db/               → session, base
  models/           → SQLAlchemy models (User, FinancialRecord)
  schemas/          → Pydantic schemas
  services/         → business logic (no DB logic in routes)
migrations/         → Alembic versions
```

---

## Setup

### 1. Clone and install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and a strong SECRET_KEY
```

### 3. Create the database

```bash
createdb finance_db
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uvicorn src.main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## Roles and Permissions

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| Login / view own profile | ✅ | ✅ | ✅ |
| View financial records | ✅ | ✅ | ✅ |
| View dashboard summaries | ❌ | ✅ | ✅ |
| Create / update / delete records | ❌ | ❌ | ✅ |
| Create / update users | ❌ | ❌ | ✅ |

---

## API Reference

### Auth

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/login` | Public | Get JWT token |
| POST | `/auth/register` | Admin | Create a new user |
| GET | `/auth/me` | Any authenticated | Get current user |

### Users

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/users` | Admin | List all users |
| GET | `/users/{id}` | Admin | Get user by ID |
| PATCH | `/users/{id}` | Admin | Update role / status |

### Financial Records

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/records` | All roles | List records (with filters) |
| GET | `/records/{id}` | All roles | Get single record |
| POST | `/records` | Admin | Create record |
| PATCH | `/records/{id}` | Admin | Update record |
| DELETE | `/records/{id}` | Admin | Soft delete record |

**Query filters for `GET /records`:**
- `type` — `income` or `expense`
- `category` — partial match (case-insensitive)
- `date_from` / `date_to` — ISO date strings (`YYYY-MM-DD`)
- `skip` / `limit` — pagination (default: 0 / 50, max limit: 200)

### Dashboard

| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/dashboard/summary` | Analyst, Admin | Total income, expenses, net balance |
| GET | `/dashboard/categories` | Analyst, Admin | Per-category totals |
| GET | `/dashboard/trends` | Analyst, Admin | Monthly income vs expense breakdown |
| GET | `/dashboard/recent` | Analyst, Admin | 5 most recent records |

**Query filters for dashboard summary, categories, trends:**
- `date_from` / `date_to` — ISO date strings (`YYYY-MM-DD`) to scope aggregations to a time range

---

## Running Tests

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

The test suite uses SQLite (no PostgreSQL needed for tests) and covers:
- Auth: login success/failure, token validation, unauthenticated access
- Records: full CRUD, soft delete, filtering by type and category
- Validation: negative amounts, missing required fields
- Role enforcement: viewer blocked from writes and dashboard, unauthenticated blocked entirely
- User management: registration, duplicate email rejection, viewer cannot register

---

## Example: First-time Setup Flow

Since `/auth/register` requires an admin token, seed the first admin directly via SQL or a one-time script:

```sql
-- password is "admin123" (bcrypt hash)
INSERT INTO users (email, full_name, hashed_password, role, is_active)
VALUES (
  'admin@example.com',
  'Admin User',
  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
  'admin',
  true
);
```

Then use `POST /auth/login` to get a token and create further users via `POST /auth/register`.

---

## Assumptions and Design Decisions

1. **Admin-only user creation** — Self-registration is disabled. Only admins can create users. This fits a controlled finance system where access is provisioned, not self-served.

2. **Soft deletes** — Records are never hard-deleted (`is_deleted = true`). This preserves audit history, which is important for financial data.

3. **Records are not user-scoped for reads** — All authenticated users can view all records. In a real multi-tenant system you'd scope by `owner_id` or organization. This is noted as a simplification.

4. **Dashboard is analyst+** — Viewers can see raw records but not aggregated insights. This reflects a common pattern where summary data is considered more sensitive than individual entries.

5. **PostgreSQL `to_char`** — Monthly trends use `to_char(date, 'YYYY-MM')` which is PostgreSQL-specific. If switching to SQLite, replace with `strftime('%Y-%m', date)`.

6. **No refresh tokens** — Kept simple with a single access token. Expiry is configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`.

7. **Pagination on records only** — Dashboard endpoints return full aggregated results (not paginated) since they're already grouped/summarized.

8. **`bcrypt==4.0.1` pinned** — The latest `bcrypt` (5.x) is incompatible with `passlib`. Pinned to 4.0.1 until passlib releases a fix. This is a known upstream issue.

9. **`created_at` on records only** — Timestamp added to `FinancialRecord` for audit trail. Not added to `User` since user lifecycle management is admin-controlled and less time-sensitive.

10. **Dashboard date filters** — All aggregation endpoints (`/summary`, `/categories`, `/trends`) accept optional `date_from` / `date_to` to scope results to a time window, useful for period-based reporting.
