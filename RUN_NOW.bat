@echo off
cd /d "%~dp0\Janun Luwum"
if exist "venv\Scripts\python.exe" (
    echo Using venv Python...
    venv\Scripts\python.exe manage.py makemigrations
    venv\Scripts\python.exe manage.py migrate
    venv\Scripts\python.exe create_superuser.py
    echo.
    echo ========================================
    echo Server starting at http://127.0.0.1:8000/
    echo Admin: http://127.0.0.1:8000/admin/
    echo Username: admin
    echo Password: admin123
    echo ========================================
    echo.
    venv\Scripts\python.exe manage.py runserver
) else (
    echo ERROR: Virtual environment not found!
    echo Please activate venv first or install Django.
    pause
)

