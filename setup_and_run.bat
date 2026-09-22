@echo off
echo ========================================
echo School Website Setup and Server Start
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Creating migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo ERROR: Failed to create migrations. Check Python installation.
    pause
    exit /b 1
)

echo.
echo Step 2: Applying migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to apply migrations.
    pause
    exit /b 1
)

echo.
echo Step 3: Creating superuser...
python create_superuser.py
if errorlevel 1 (
    echo ERROR: Failed to create superuser.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Admin Credentials:
echo   Username: admin
echo   Password: admin123
echo.
echo Starting server...
echo.
echo Access URLs:
echo   Website: http://127.0.0.1:8000/
echo   Admin:   http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause

