@echo off
cd /d "%~dp0\Janun Luwum"
python -m pip install django==5.2.8 pillow==12.0.0 django-ckeditor==6.7.3 --user
python manage.py makemigrations
python manage.py migrate
python create_superuser.py
echo.
echo Server starting at http://127.0.0.1:8000/
echo Admin: http://127.0.0.1:8000/admin/
echo Username: admin
echo Password: admin123
echo.
python manage.py runserver
pause

