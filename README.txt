----------------------------------------
Create the Database and Migrations:
# Create fresh migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

#Apply seed_dummy_users
python manage.py seed_dummy_users

---------------------------------------
Run the Server:
python manage.py runserver

Ensure the Command Runs Continuously:
start python manage.py run_scheduled_outbounds

Run Celery Worker and Beat:
celery -A warehouse_management worker -l info

celery -A warehouse_management beat -l info

