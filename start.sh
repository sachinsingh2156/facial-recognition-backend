#!/bin/bash
# Wait for database to be ready (if using external DB)
# Apply migrations
python facial_recognition_system/manage.py migrate

# Start the Django server
python facial_recognition_system/manage.py runserver 0.0.0.0:8053
