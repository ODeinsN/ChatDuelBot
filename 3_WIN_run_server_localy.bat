@echo off
cd CBDGUI
call "../venv/Scripts/activate" && python manage.py runserver
pause