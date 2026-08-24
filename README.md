# Finvoro

A personal finance management API and web app built with Django, Django REST Framework, and PostgreSQL. Users can track accounts, categorize income and expenses, set monthly budgets, and view spending reports : all behind JWT-authenticated, per-user-scoped endpoints.

Built as a learning project to practice production-grade Django backend patterns: REST API design, JWT auth, PostgreSQL constraints and indexes, query optimization, and automated testing.

## Features

- **Accounts** : bank, cash, wallet, or credit card accounts with a live-computed current balance (initial balance + income − expenses, never a stale duplicated value).
- **Categories** : system-wide defaults (Food, Salary, Rent, ...) plus user-created custom categories, each typed as INCOME or EXPENSE.
- **Transactions** : the core feature: filterable by category, account, type, and date range; paginated; ownership-enforced end to end.
- **Budgets** : monthly per-category budgets with computed spent/remaining/percentage-used.
- **Reports** : monthly summary, month-by-month breakdown, category-wise spending, and per-account balances.
- **Frontend** : a small vanilla HTML/CSS/JS app (served by Django itself, same-origin) covering register/login/dashboard/accounts/transactions/budgets.
- **API docs** : interactive Swagger UI and ReDoc via `drf-spectacular`.

## Tech stack

Python, Django, Django REST Framework, PostgreSQL, JWT (`djangorestframework-simplejwt`), HTML/CSS/vanilla JS, `django-filter`, `drf-spectacular`, `pytest`/`pytest-django`. No Docker, no React, no Node backend.

## Project structure

```
config/            Django project settings, root URLs
apps/
  users/           Custom User model, JWT auth endpoints
  accounts/        Financial accounts (bank/cash/wallet/credit card)
  categories/      Income/expense categories (default + user-owned)
  transactions/    Income/expense transactions
  budgets/         Monthly category budgets
  reports/         Read-only aggregation endpoints
frontend/          HTML templates (extend base.html)
static/            CSS and vanilla JS
```

## Local setup

1. **PostgreSQL**: create a database and a dedicated role (don't use the `postgres` superuser for the app):
   ```sql
   CREATE DATABASE finvoro;
   CREATE USER finvoro_user WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE finvoro TO finvoro_user;
   \c finvoro
   GRANT ALL ON SCHEMA public TO finvoro_user;
   ```

2. **Environment**: copy `.env.example` to `.env` and fill in your values.

3. **Install and migrate**:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run**:
   ```bash
   python manage.py runserver
   ```
   - App: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/
   - API docs: http://127.0.0.1:8000/api/docs/

## Testing

```bash
pytest                                    # run the suite
pytest --cov=apps --cov-report=term-missing   # with coverage
```

## API overview

All endpoints are versioned under `/api/v1/` and (except register/login/refresh) require a JWT `Authorization: Bearer <token>` header. Every list endpoint is scoped to the authenticated user and paginated.

```
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/
POST   /api/v1/auth/refresh/
GET    /api/v1/auth/me/

GET|POST      /api/v1/accounts/
GET|PATCH|DELETE  /api/v1/accounts/{id}/

GET|POST      /api/v1/categories/
GET|PATCH|DELETE  /api/v1/categories/{id}/

GET|POST      /api/v1/transactions/          ?category=&account=&transaction_type=&start_date=&end_date=&ordering=
GET|PATCH|DELETE  /api/v1/transactions/{id}/

GET|POST      /api/v1/budgets/               ?category=&month=&year=
GET|PATCH|DELETE  /api/v1/budgets/{id}/

GET  /api/v1/reports/summary/                ?month=&year=
GET  /api/v1/reports/monthly/                ?year=
GET  /api/v1/reports/categories/             ?month=&year=&transaction_type=
GET  /api/v1/reports/accounts/
```

Full interactive documentation (request/response schemas, try-it-out) is available at `/api/docs/` once the server is running.

## Deployment

No Docker : standard Django deployment. The project ships with `gunicorn` (WSGI server) and `whitenoise` (serves static files directly, no separate static host needed) and a `Procfile` for platforms that read one (Render, Railway, Heroku-style). In production, set `DJANGO_DEBUG=False` in your environment : this automatically enables secure cookies and SSL redirect (see `config/settings.py`).

Note: `gunicorn` requires a Unix-like OS (it depends on the `fcntl` module) : it will not run on Windows. Use `python manage.py runserver` for local development on Windows; deploy to a Linux-based host for production.
