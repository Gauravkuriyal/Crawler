@echo off
REM Change to your Django project directory (where manage.py is)
REM %~dp0 gets the directory of the batch file itself
cd /d "%~dp0"

REM Activate the virtual environment
REM Adjust the path if your venv is named differently or in a different location
call venv\Scripts\activate.bat

echo Starting Django development server...
echo Opening browser in 3 seconds...

REM Open the browser
start "" "http://127.0.0.1:8000/"

REM Wait for a few seconds for the server to start
timeout /t 3 /nobreak >nul

REM Run the Django development server
REM This command will keep the terminal window open and display server logs
python manage.py runserver