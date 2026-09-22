#!/usr/bin/env python
"""Script to create a superuser non-interactively"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_website.settings')
django.setup()

from django.contrib.auth.models import User

# Check if admin user already exists
if User.objects.filter(username='admin').exists():
    print("Admin user already exists!")
    admin = User.objects.get(username='admin')
    print(f"Username: {admin.username}")
    print(f"Email: {admin.email if admin.email else '(no email)'}")
    print(f"Is Superuser: {admin.is_superuser}")
    print(f"Is Active: {admin.is_active}")
else:
    # Create superuser
    try:
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@school.ug',
            password='admin123'
        )
        print("=" * 60)
        print("SUPERUSER CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
        print()
        print("⚠️  IMPORTANT: Change this password after first login!")
        print("=" * 60)
    except Exception as e:
        print(f"Error creating superuser: {e}")
        sys.exit(1)

