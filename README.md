# School Website - Kamuganguzi Janan Luwum Memorial Senior Secondary School

A comprehensive Django-based school website with full CRUD operations, integrated with the dotShule government portal.

## Features

- **Home Page** with headteacher video message
- **News Section** with search and pagination
- **Announcements** with priority levels
- **Photo Gallery** with category filtering
- **Staff Directory** with department filtering
- **Departments** information
- **Events Calendar**
- **Contact Form**
- **Custom Pages** (About, Academics, etc.)
- **dotShule Portal Integration** for teacher/student login
- **Full Admin Panel** with CRUD operations for all content
- **Modern Blue & White Design** by Twiina Technologies

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

6. Access admin panel at: http://127.0.0.1:8000/admin/

## Admin Features

The admin panel allows you to manage:
- School Information (name, logo, address, about, vision, mission)
- Headteacher Video Messages
- News Articles
- Announcements
- Photo Gallery
- Departments
- Staff Members
- Events
- Contact Messages
- Custom Pages

## dotShule Integration

Teachers and students can login via the government portal at https://dotshule.ug/. The login button redirects to the configured dotShule URL.

## Design

- Color Scheme: Blue (#1e3a8a, #3b82f6) and White
- Responsive Bootstrap 5 design
- Modern UI with smooth animations
- Font Awesome icons
- Google Fonts (Poppins)

## Development

Designed and developed by **Twiina Technologies**

