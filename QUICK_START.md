# Quick Start Guide

## First Time Setup

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Initialize School Data**
   ```bash
   python manage.py init_school
   ```
   This creates the basic school information and default pages.

3. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

4. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access the Website**
   - Frontend: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Admin Panel Setup

After logging into the admin panel:

1. **School Information** - Add/Edit:
   - School name, logo, motto
   - Address, phone, email
   - About, Vision, Mission
   - dotShule URL

2. **Headteacher Message** - Add:
   - Title
   - Video URL (YouTube embed URL)
   - Thumbnail image (optional)
   - Message text

3. **News** - Create news articles:
   - Title, content, image
   - Mark as featured if needed
   - Publish when ready

4. **Announcements** - Create announcements:
   - Set priority (High, Medium, Low)
   - Add expiration date if needed

5. **Gallery** - Upload photos:
   - Add category for organization
   - Mark as featured for homepage

6. **Departments** - Add school departments:
   - Name, description, head
   - Icon (Font Awesome class)

7. **Staff** - Add staff members:
   - Name, position, department
   - Photo, email, phone, bio

8. **Events** - Add upcoming events:
   - Title, description, date/time
   - Location, image

9. **Pages** - Create custom pages:
   - About, Academics, etc.
   - Use slug for URL (e.g., 'about' for /page/about/)

## Features Overview

- ✅ Home page with headteacher video message
- ✅ News section with search and pagination
- ✅ Announcements with priority levels
- ✅ Photo gallery with categories
- ✅ Staff directory
- ✅ Departments information
- ✅ Events calendar
- ✅ Contact form
- ✅ Custom pages
- ✅ dotShule portal integration
- ✅ Full admin CRUD operations
- ✅ Beautiful blue & white design

## Notes

- All content can be managed through the admin panel
- Teachers/Students login via dotShule portal (configured in School Info)
- The website is fully responsive and mobile-friendly
- Designed by Twiina Technologies

