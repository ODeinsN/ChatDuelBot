@echo off
pip install virtualenv
python -m venv venv
call "venv/Scripts/activate.bat" &&  pip install -r requirements.txt
pause