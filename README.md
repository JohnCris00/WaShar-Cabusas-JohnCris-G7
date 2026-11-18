# WaShar

Car wash finder and time-slot reservation system. Full-stack Django (templates) + PostgreSQL/Supabase.

## Phase 1: Account feature
Registration, login/logout, role-based dashboards (Vehicle owner / Shop operator), and profile view/edit.

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # then fill in your database credentials and SECRET_KEY
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Supabase: use the connection details from Project Settings > Database and set `DB_SSLMODE=require`.

## Routes
| URL | Access |
|---|---|
| `/register/`, `/login/` | Public |
| `/dashboard/` | Logged in; redirects by role |
| `/dashboard/customer/` | Vehicle owners only |
| `/dashboard/operator/` | Shop operators only |
| `/profile/`, `/profile/edit/` | Logged in (own profile only) |
