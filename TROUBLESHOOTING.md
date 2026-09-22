# Troubleshooting Guide

## Server is Running but Page Appears Blank

If the server is running but you see a blank page, try these steps:

### 1. Clear Browser Cache
- **Chrome/Edge**: Press `Ctrl+Shift+Delete` (or `Cmd+Shift+Delete` on Mac)
- **Firefox**: Press `Ctrl+Shift+Delete` (or `Cmd+Shift+Delete` on Mac)
- Select "Cached images and files" and clear

### 2. Hard Refresh
- **Windows/Linux**: Press `Ctrl+F5` or `Ctrl+Shift+R`
- **Mac**: Press `Cmd+Shift+R`

### 3. Check Browser Console
- Press `F12` to open Developer Tools
- Go to the "Console" tab
- Look for any JavaScript errors (red text)
- Go to the "Network" tab and check if CSS/JS files are loading

### 4. Verify Server is Running
```bash
# Check if server is running
curl http://127.0.0.1:8000/

# Or visit in browser:
# http://127.0.0.1:8000/
# http://localhost:8000/
```

### 5. Check Server Logs
The server logs will show any errors. Look for:
- Template errors
- Database errors
- Import errors

### 6. Restart the Server
```bash
# Stop any running server
pkill -f "manage.py runserver"

# Start fresh
cd "/home/evinia/Documents/Janun Luwum"
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

## Common Issues

### Issue: "TemplateDoesNotExist" error
**Solution**: Make sure templates are in the correct location:
- Templates should be in: `templates/school/`
- Check `settings.py` has `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`

### Issue: Static files not loading
**Solution**: 
```bash
python manage.py collectstatic --noinput
```

### Issue: Database errors
**Solution**:
```bash
python manage.py migrate
```

### Issue: Context processor errors
**Solution**: The context processor has been updated to handle errors gracefully. If issues persist, check:
- Database is migrated: `python manage.py migrate`
- SchoolInfo exists: Run `python manage.py init_school` if needed

## Quick Start Commands

```bash
# Navigate to project
cd "/home/evinia/Documents/Janun Luwum"

# Activate virtual environment
source venv/bin/activate

# Run migrations (if needed)
python manage.py migrate

# Collect static files (if needed)
python manage.py collectstatic --noinput

# Start server
python manage.py runserver 0.0.0.0:8000
```

Or use the startup script:
```bash
./start_server.sh
```

## Access URLs

- **Homepage**: http://127.0.0.1:8000/ or http://localhost:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **News**: http://127.0.0.1:8000/news/
- **Contact**: http://127.0.0.1:8000/contact/

## Admin Access

To access the admin panel:
1. Create a superuser (if not already created):
   ```bash
   python manage.py createsuperuser
   ```
2. Visit: http://127.0.0.1:8000/admin/
3. Login with your superuser credentials

## Still Having Issues?

1. Check the terminal where the server is running for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Make sure you're using the correct Python version (3.8+)

