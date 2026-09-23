"""
admissions/urls.py — URLs for JLMSSS Admission Portal v2
Mounted natively under the admission subdomain via middleware.
"""

from django.urls import path
from . import views

app_name = 'admissions'

admissions_patterns = (
    [
        # Public & Auth
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('verify/<str:token>/', views.verify_email_view, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
    # Resend Verification
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    
    # Parent / Guardian Dashboard & Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('student/add/', views.add_student_view, name='add_student'),
    path('student/<int:student_id>/edit/', views.edit_student_view, name='edit_student'),
    
    # Application Flow
    path('start/<int:window_id>/<int:student_id>/', views.start_application_view, name='start_application'),
    path('application/<str:app_number>/', views.status_detail_view, name='status_detail'),
    path('application/<str:app_number>/form/', views.application_form_view, name='application_form'),
    path('application/<str:app_number>/upload/', views.document_upload_view, name='document_upload'),
    path('application/<str:app_number>/upload/<str:slot_key>/', views.upload_document_ajax, name='upload_document_ajax'),
    path('application/<str:app_number>/delete-doc/<int:doc_id>/', views.delete_document_ajax, name='delete_document_ajax'),
    path('application/<str:app_number>/transfer/', views.transfer_info_view, name='transfer_info'),
    path('application/<str:app_number>/payment/', views.payment_view, name='payment'),
    path('application/<str:app_number>/submit/', views.submit_application_view, name='submit_application'),
    
    # Post-submission Actions
    path('application/<str:app_number>/accept-offer/', views.accept_offer_view, name='accept_offer'),
    path('application/<str:app_number>/receipt/', views.download_receipt_view, name='download_receipt'),
    path('application/<str:app_number>/offer-letter/', views.download_offer_letter_view, name='download_offer_letter'),

    # ========================================================================
    # ADMIN STAFF PORTAL (Separate from Django Admin)
    # ========================================================================
    path('staff/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/directory/', views.staff_directory_view, name='staff_directory'),
    path('staff/export/', views.staff_export_csv_view, name='staff_export_csv'),
    
    path('staff/app/<str:app_number>/', views.staff_review_view, name='staff_review'),
    path('staff/app/<str:app_number>/change-status/', views.staff_change_status_view, name='staff_change_status'),
    path('staff/app/<str:app_number>/send-feedback/', views.staff_send_feedback_view, name='staff_send_feedback'),
    path('staff/app/<str:app_number>/generate-offer/', views.staff_generate_offer_view, name='staff_generate_offer'),
    
    # Document Review endpoints
    path('staff/doc/<int:doc_id>/approve/', views.staff_approve_document_view, name='staff_approve_document'),
    path('staff/doc/<int:doc_id>/flag/', views.staff_flag_document_view, name='staff_flag_document'),
    ],
    'admissions'
)

from django.urls import include
urlpatterns = [ path('', include(admissions_patterns, namespace='admissions')) ]
