"""
helpdesk/urls.py

URL configuration for the helpdesk app.

Mount this in the project's root urls.py with a prefix, e.g.:
    path('help/', include('helpdesk.urls')),
"""

from django.urls import path
from . import views

app_name = 'helpdesk'

urlpatterns = [
    # ------------------------------------------------------------------ #
    # Public AJAX endpoints (no authentication required)
    # ------------------------------------------------------------------ #

    # Create or retrieve a help session by browser-generated UUID.
    path('start/', views.start_session, name='helpdesk_start'),

    # Send a message into an existing session.
    path('send/', views.send_message, name='helpdesk_send'),

    # Poll for new messages in a session (long-polling friendly).
    path('messages/<str:session_key>/', views.get_messages, name='helpdesk_messages'),

    # End / terminate chat session by visitor.
    path('close/', views.visitor_close_session, name='helpdesk_visitor_close'),

    # ------------------------------------------------------------------ #
    # Staff-only endpoints (requires is_staff)
    # ------------------------------------------------------------------ #

    # Dashboard: list all help sessions.
    path('admin-desk/', views.admin_sessions, name='helpdesk_admin_sessions'),

    # Detail / reply view for a single session.
    path('admin-desk/<int:session_id>/', views.admin_session_detail, name='helpdesk_admin_detail'),

    # Close / resolve a session.
    path('admin-desk/<int:session_id>/close/', views.close_session, name='helpdesk_close'),
]
