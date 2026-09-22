#!/usr/bin/env python
"""Script to check and display admin credentials"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_website.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("ADMIN PANEL CREDENTIALS")
print("=" * 60)
print()

superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    print(f"Found {superusers.count()} superuser(s):\n")
    for i, user in enumerate(superusers, 1):
        print(f"Admin #{i}:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email if user.email else '(no email set)'}")
        print(f"  Active: {'Yes' if user.is_active else 'No'}")
        print(f"  Last Login: {user.last_login if user.last_login else 'Never'}")
        print()
else:
    print("❌ No superuser found!")
    print()
    print("To create a superuser, run:")
    print("  python manage.py createsuperuser")
    print()
    print("Or use this script to create one automatically:")
    print("  python create_admin.py")

print("=" * 60)
print("Admin Panel URL: http://127.0.0.1:8000/admin/")
print("=" * 60)

