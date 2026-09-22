# Migration Instructions

## Important: Run Migrations After Model Updates

The `HeadteacherMessage` model has been updated to support multiple administrator video messages. You need to create and run migrations.

## Steps to Apply Changes

1. **Navigate to the project directory:**
   ```bash
   cd "Janun Luwum"
   ```

2. **Activate virtual environment (if using one):**
   ```bash
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   
   # On Windows CMD:
   venv\Scripts\activate.bat
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Create migrations:**
   ```bash
   python manage.py makemigrations
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

## What Changed in the Model

The `HeadteacherMessage` model now includes:
- `admin_type` field - Type of administrator (Headteacher, Deputy, Principal, etc.)
- `admin_name` field - Optional name of the administrator
- `order` field - Display order for multiple messages

These changes allow you to add multiple video messages from different school administrators, not just the headteacher.

## After Migration

1. Go to the admin panel: http://127.0.0.1:8000/admin/
2. Navigate to **Administrator Video Messages**
3. You can now add multiple messages with different administrator types
4. Use the "Order" field to control which messages appear first

## Troubleshooting

If you get errors:
- Make sure you're in the correct directory
- Ensure the virtual environment is activated
- Check that Django is installed: `pip install -r requirements.txt`
- Verify the database is set up: `python manage.py migrate` (without makemigrations first)

