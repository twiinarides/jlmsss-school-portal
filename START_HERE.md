# 🚀 Quick Start Guide

## The Server is Already Running!

Your Django server is currently running. You can access it at:

### 🌐 Access URLs:
- **Main Website**: http://127.0.0.1:8000/
- **Alternative**: http://localhost:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## If You See a Blank Page:

### Step 1: Clear Browser Cache
1. Press `Ctrl+Shift+Delete` (or `Cmd+Shift+Delete` on Mac)
2. Select "Cached images and files"
3. Click "Clear data"

### Step 2: Hard Refresh
- **Windows/Linux**: Press `Ctrl+F5` or `Ctrl+Shift+R`
- **Mac**: Press `Cmd+Shift+R`

### Step 3: Check Browser Console
1. Press `F12` to open Developer Tools
2. Click the "Console" tab
3. Look for any red error messages
4. If you see errors, take a screenshot and check the troubleshooting guide

### Step 4: Verify Server is Running
Open a new terminal and run:
```bash
curl http://127.0.0.1:8000/
```

If you see HTML content, the server is working correctly.

## Restart the Server (if needed):

```bash
# Stop the current server
pkill -f "manage.py runserver"

# Navigate to project
cd "/home/evinia/Documents/Janun Luwum"

# Activate virtual environment
source venv/bin/activate

# Start server
python manage.py runserver 0.0.0.0:8000
```

Or use the startup script:
```bash
./start_server.sh
```

## What You Should See:

When you visit http://127.0.0.1:8000/, you should see:
- ✅ A blue navigation bar at the top
- ✅ "Welcome to Kamuganguzi Janan Luwum Memorial Senior Secondary School"
- ✅ Navigation links (Home, News, Announcements, etc.)
- ✅ A footer at the bottom

## Admin Panel Access:

1. Visit: http://127.0.0.1:8000/admin/
2. Login with your superuser credentials
3. If you haven't created a superuser yet:
   ```bash
   python manage.py createsuperuser
   ```

## Need Help?

Check `TROUBLESHOOTING.md` for detailed troubleshooting steps.

