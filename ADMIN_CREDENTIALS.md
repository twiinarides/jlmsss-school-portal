# Admin Panel Login Details

## Accessing the Admin Panel

1. **URL**: http://127.0.0.1:8000/admin/
2. **Alternative**: http://localhost:8000/admin/

## Creating a Superuser (If Not Already Created)

If you don't have admin credentials yet, create a superuser by running:

```bash
cd "Janun Luwum"
python manage.py createsuperuser
```

You will be prompted to enter:
- Username
- Email address (optional)
- Password (twice for confirmation)

## Default Admin Credentials

**Note**: If a superuser already exists, you can check it by running:

```bash
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth.models import User
users = User.objects.filter(is_superuser=True)
for u in users:
    print(f"Username: {u.username}, Email: {u.email}")
```

## Recommended Admin Credentials

For security, it's recommended to create your own superuser with a strong password. However, if you need default credentials for initial setup, you can use:

**Username**: `admin`  
**Password**: `admin123` (CHANGE THIS IMMEDIATELY after first login)

**To set this up, run:**
```bash
python manage.py shell
```

Then:
```python
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@school.ug', 'admin123')
```

**⚠️ IMPORTANT**: Change the default password immediately after first login for security!

## Admin Panel Features

Once logged in, you can manage:

1. **School Information** - Update logo, name, address, contact info, about, vision, mission
2. **Administrator Video Messages** - Add video messages from headteacher, deputy, principal, etc.
3. **News Articles** - Create and manage news posts
4. **Announcements** - Post important announcements
5. **Photo Gallery** - Upload and organize photos
6. **Departments** - Manage school departments
7. **Staff Members** - Add staff with photos, contact numbers, and email addresses
8. **Events** - Create and manage school events
9. **Contact Messages** - View messages from the contact form
10. **Custom Pages** - Create additional pages (About, Academics, etc.)

## Logo Management

To update the school logo:

1. Go to **School Information** in the admin panel
2. Click on the existing school entry (or create one if it doesn't exist)
3. Upload a new logo image in the "Logo" field
4. Click **Save**

The logo will automatically appear in the navbar (replacing the school name text) and can be updated anytime through the admin panel.

## Staff Contact Information

To add staff with contact numbers:

1. Go to **Staff** in the admin panel
2. Click **Add Staff Member**
3. Fill in:
   - First Name and Last Name
   - Position (Headteacher, Deputy, Teacher, etc.)
   - Department (optional)
   - **Phone** - This will be displayed publicly on the staff page
   - **Email** - This will also be displayed publicly
   - Photo (optional)
   - Bio (optional)
4. Click **Save**

All staff contact information (phone and email) is publicly visible on the staff directory page for visitors' convenience.

## Administrator Video Messages

To add video messages from school administrators:

1. Go to **Administrator Video Messages** in the admin panel
2. Click **Add Administrator Video Message**
3. Fill in:
   - Title
   - Administrator Type (Headteacher, Deputy Headteacher, Principal, Director, etc.)
   - Administrator Name (optional)
   - Video URL (YouTube embed URL)
   - Thumbnail (optional)
   - Message (accompanying text)
   - Order (display order - lower numbers appear first)
4. Click **Save**

Multiple video messages will appear on the home page in the "Messages from School Leadership" section.

## Troubleshooting

If you cannot log in:

1. Make sure the server is running: `python manage.py runserver`
2. Verify you're using the correct URL: http://127.0.0.1:8000/admin/
3. Check that a superuser exists (see instructions above)
4. Try creating a new superuser if needed
5. Clear browser cache and cookies
6. Try a different browser or incognito mode

## Security Notes

- Always use a strong password for admin accounts
- Change default passwords immediately
- Don't share admin credentials publicly
- Consider using environment variables for sensitive settings in production

