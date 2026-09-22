# 🚀 Complete Setup Instructions

## Quick Setup (Windows)

### Option 1: Use the Batch File (Easiest)

1. **Double-click** `setup_and_run.bat` in the `Janun Luwum` folder
2. Wait for setup to complete
3. Server will start automatically
4. Open browser to: http://127.0.0.1:8000/

### Option 2: Manual Setup

Open PowerShell or Command Prompt in the `Janun Luwum` folder and run:

```powershell
# Step 1: Create migrations
python manage.py makemigrations

# Step 2: Apply migrations
python manage.py migrate

# Step 3: Create superuser
python create_superuser.py

# Step 4: Start server
python manage.py runserver
```

## Admin Credentials

After running the setup:

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@school.ug`

⚠️ **IMPORTANT**: Change the password after first login!

## Access URLs

- **Main Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## If Python is Not Found

If you get "Python was not found":

1. **Check if Python is installed**:
   - Open Command Prompt
   - Type: `python --version`
   - If not found, install Python from python.org

2. **Use Python from venv** (if virtual environment exists):
   ```powershell
   .\venv\Scripts\activate
   python manage.py makemigrations
   python manage.py migrate
   python create_superuser.py
   python manage.py runserver
   ```

3. **Use full Python path**:
   ```powershell
   C:\Python\python.exe manage.py makemigrations
   C:\Python\python.exe manage.py migrate
   C:\Python\python.exe create_superuser.py
   C:\Python\python.exe manage.py runserver
   ```

## What the Setup Does

1. **makemigrations**: Creates database migration files for model changes
2. **migrate**: Applies database changes (adds new fields to HeadteacherMessage)
3. **create_superuser**: Creates admin user with credentials:
   - Username: admin
   - Password: admin123
4. **runserver**: Starts Django development server

## After Setup

1. **Login to Admin Panel**: http://127.0.0.1:8000/admin/
2. **Upload School Logo**: 
   - Go to "School Information"
   - Upload logo image
   - Save
3. **Add Staff**: 
   - Go to "Staff"
   - Add staff members with phone numbers and emails
4. **Add Administrator Video Messages**:
   - Go to "Administrator Video Messages"
   - Add video messages from different administrators
5. **Update School Profile**:
   - Go to "School Information"
   - Update About, Vision, Mission

## Troubleshooting

### Migration Errors
- Make sure you're in the correct directory: `Janun Luwum`
- Check that `db.sqlite3` file exists
- Try: `python manage.py migrate --run-syncdb`

### Superuser Already Exists
- If admin user already exists, the script will show existing credentials
- You can still use those credentials to login

### Port Already in Use
- If port 8000 is busy, use: `python manage.py runserver 8001`
- Then access: http://127.0.0.1:8001/

### Database Errors
- Delete `db.sqlite3` and run migrations again
- Or check file permissions

## Testing the Website

After server starts, test these pages:

1. **Home Page**: http://127.0.0.1:8000/
   - Check logo appears (not school name)
   - Check staff directory with contact numbers
   - Check administrator video messages section
   - Check varied colors (green, orange, purple)

2. **Staff Page**: http://127.0.0.1:8000/staff/
   - Check phone numbers are prominently displayed
   - Check phone numbers are clickable
   - Check email addresses are clickable

3. **Admin Panel**: http://127.0.0.1:8000/admin/
   - Login with admin/admin123
   - Check all sections are accessible
   - Upload logo
   - Add staff with contact info

## Features to Verify

- [ ] Logo appears in navbar (not long school name)
- [ ] Home page shows all sections correctly
- [ ] Staff contact information is publicly visible
- [ ] Phone numbers are clickable (tel: links)
- [ ] Email addresses are clickable (mailto: links)
- [ ] Multiple administrator video messages can be added
- [ ] Colors are varied (not just blue)
- [ ] Design looks professional and natural
- [ ] All pages are responsive

## Need Help?

- Check `QUICK_START_GUIDE.md` for detailed instructions
- Check `ADMIN_CREDENTIALS.md` for admin access help
- Check `COMPLETE_IMPLEMENTATION_DETAILS.md` for technical details

