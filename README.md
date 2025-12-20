## Disclaimer

This project is created **strictly for testing, educational, and experimental purposes**.
It is **not intended for commercial use**.
The project is for **personal use only**, and the author retains **all rights** to the code and content.

---

## User Roles

The system supports **three types of users**:

* **Admin**
* **Manager**
* **Operator**

---

## Default Login Credentials

For development and testing purposes, the following default credentials are available:

| Role     | Username   |
| -------- | ---------- |
| Admin    | `admin`    |
| Manager  | `manager`  |
| Operator | `operator` |

---

## Database Setup and Migrations

Run the following commands in order to set up the database:

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to the database
python manage.py migrate

# Seed the database with dummy users
python manage.py seed_dummy_users
```

---

## Running the Server

Start the Django development server:

```bash
python manage.py runserver
```

---

## Running Scheduled Commands

Ensure the scheduled outbound process runs continuously:

```bash
python manage.py run_scheduled_outbounds
```

---

## Running Celery

Start the Celery worker and beat scheduler in separate terminals:

```bash
# Start Celery worker
celery -A warehouse_management worker -l info

# Start Celery beat
celery -A warehouse_management beat -l info
```


