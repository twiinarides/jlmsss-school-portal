"""
admissions/utils.py — Utility helpers for JLMSSS Admission Portal v2
"""

import csv
import io
import uuid
from django.utils import timezone


def generate_application_number(window=None):
    """Generate unique application number: JLMSSS-YYYY-NNNNNN"""
    from .models import Application
    year = timezone.now().year
    prefix = f'JLMSSS-{year}-'
    last = Application.objects.filter(
        application_number__startswith=prefix
    ).order_by('-application_number').first()
    last_num = 0
    if last:
        try:
            last_num = int(last.application_number.split('-')[-1])
        except (ValueError, IndexError):
            last_num = 0
    return f'{prefix}{str(last_num + 1).zfill(6)}'


def generate_verification_token():
    return uuid.uuid4().hex + uuid.uuid4().hex[:32]


def get_status_badge(status):
    """Bootstrap badge color class for application status."""
    mapping = {
        'draft': 'secondary',
        'submitted': 'info',
        'under_doc_review': 'primary',
        'action_required': 'warning',
        'docs_resubmitted': 'info',
        'approved': 'success',
        'provisionally_admitted': 'success',
        'enrolled': 'success',
        'rejected': 'danger',
        'withdrawn': 'dark',
        'payment_pending': 'warning',
        'shortlisted': 'primary',
    }
    return mapping.get(status, 'secondary')


def get_status_icon(status):
    """Font Awesome icon for application status."""
    mapping = {
        'draft': 'fas fa-pen',
        'submitted': 'fas fa-paper-plane',
        'under_doc_review': 'fas fa-search',
        'action_required': 'fas fa-exclamation-triangle',
        'docs_resubmitted': 'fas fa-redo',
        'approved': 'fas fa-check-circle',
        'provisionally_admitted': 'fas fa-graduation-cap',
        'enrolled': 'fas fa-school',
        'rejected': 'fas fa-times-circle',
        'withdrawn': 'fas fa-ban',
    }
    return mapping.get(status, 'fas fa-circle')


def export_applications_csv(queryset):
    """Convert Application queryset to CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Application #', 'Student Name', 'Account Holder', 'Email', 'Phone',
        'Class', 'Window', 'Status', 'Transfer', 'Submitted At',
        'Payment Ref', 'Payment Verified', 'Documents Approved',
    ])
    for app in queryset.select_related('applicant__user', 'window', 'student'):
        docs = app.documents.all()
        all_approved = not docs.filter(status__in=['pending', 'flagged']).exists() if docs.exists() else False
        writer.writerow([
            app.application_number,
            app.student_name,
            app.applicant.full_name,
            app.applicant.user.email,
            app.applicant.phone,
            app.get_entry_class_display(),
            str(app.window),
            app.get_status_display(),
            'Yes' if app.is_transfer else 'No',
            app.submitted_at.strftime('%Y-%m-%d %H:%M') if app.submitted_at else '',
            app.payment_reference,
            'Yes' if app.payment_verified else 'No',
            'Yes' if all_approved else 'No',
        ])
    return output.getvalue()


def log_audit(staff_user, action, application=None, details='', request=None):
    """Create an AuditLog entry."""
    try:
        from .models import AuditLog
        ip = None
        if request:
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.META.get('REMOTE_ADDR')
        AuditLog.objects.create(
            staff=staff_user,
            application=application,
            action=action,
            details=details,
            ip_address=ip,
        )
    except Exception:
        pass


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
