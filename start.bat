@echo off
python facial_recognition_system/manage.py migrate
python facial_recognition_system/manage.py runserver 0.0.0.0:8053
