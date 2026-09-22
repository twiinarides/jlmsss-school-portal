"""
admissions/email_utils.py — Transactional email functions for JLMSSS Admission Portal
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

ADMISSION_EMAIL_FROM = getattr(settings, 'ADMISSION_EMAIL_FROM', 'admissions@jananluwummemorialsss.sc.ug')
ADMISSION_SUBDOMAIN = getattr(settings, 'ADMISSION_SUBDOMAIN', 'https://admission.jananluwummemorialsss.sc.ug')


def _send(subject, to_email, html_template, context, text_fallback=None, attachment=None):
    """Internal helper: send a single HTML email, log result."""
    try:
        context['portal_url'] = ADMISSION_SUBDOMAIN
        context['school_name'] = 'Kamuganguzi Janan Luwum Memorial Senior Secondary School'
        html_body = render_to_string(html_template, context)
        text_body = text_fallback or 'Please view this email in an HTML-capable client.'
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=ADMISSION_EMAIL_FROM,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        if attachment:
            filename, content, mimetype = attachment
            msg.attach(filename, content, mimetype)
        msg.send(fail_silently=False)
        _log_notification(to_email, subject, html_body[:500], 'sent')
        return True
    except Exception as exc:
        logger.error('Admission email failed to %s: %s', to_email, exc)
        _log_notification(to_email, subject, '', 'failed', str(exc))
        return False


def _log_notification(email, subject, body_preview, status, error=''):
    """Silently log notification without crashing if DB isn't ready."""
    try:
        from .models import NotificationLog
        NotificationLog.objects.create(
            recipient_email=email,
            channel='email',
            subject=subject,
            body_preview=body_preview[:500],
            status=status,
            error_message=error,
        )
    except Exception:
        pass


# ============================================================================
# AUTH EMAILS
# ============================================================================

def send_verification_email(user, token):
    """Send email address verification link to new registrant."""
    verify_url = f'{ADMISSION_SUBDOMAIN}/verify/{token.token}/'
    subject = 'Verify Your Email — JLMSSS Admissions Portal'
    context = {
        'user': user,
        'verify_url': verify_url,
        'expires_hours': 48,
    }
    return _send(subject, user.email, 'admissions/emails/verification.html', context)


def send_welcome_email(user):
    """Send welcome email after account is activated."""
    subject = 'Welcome to JLMSSS Admissions Portal'
    context = {'user': user, 'dashboard_url': f'{ADMISSION_SUBDOMAIN}/dashboard/'}
    return _send(subject, user.email, 'admissions/emails/welcome.html', context)


def send_password_reset_email(user, token):
    """Send password reset link."""
    reset_url = f'{ADMISSION_SUBDOMAIN}/reset-password/{token.token}/'
    subject = 'Password Reset Request — JLMSSS Admissions'
    context = {'user': user, 'reset_url': reset_url, 'expires_hours': 2}
    return _send(subject, user.email, 'admissions/emails/password_reset.html', context)


# ============================================================================
# APPLICATION STATUS EMAILS
# ============================================================================

def send_submission_confirmation(application):
    """Send confirmation that application was successfully submitted."""
    subject = f'Application Received — {application.application_number}'
    status_url = f'{ADMISSION_SUBDOMAIN}/application/{application.application_number}/status/'
    context = {
        'application': application,
        'student_name': application.student_name,
        'status_url': status_url,
    }
    email = application.applicant.user.email
    return _send(subject, email, 'admissions/emails/submission_confirmation.html', context)


def send_status_change_email(application, old_status, new_status, note=''):
    """Send notification when application status changes."""
    status_url = f'{ADMISSION_SUBDOMAIN}/application/{application.application_number}/status/'
    status_labels = dict([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_doc_review', 'Under Document Review'),
        ('action_required', 'Action Required — Resubmission Needed'),
        ('docs_resubmitted', 'Documents Resubmitted'),
        ('approved', 'Approved'),
        ('provisionally_admitted', 'Provisionally Admitted'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ])
    subject = f'Application Update: {status_labels.get(new_status, new_status)} — {application.application_number}'
    context = {
        'application': application,
        'student_name': application.student_name,
        'old_status': status_labels.get(old_status, old_status),
        'new_status': status_labels.get(new_status, new_status),
        'new_status_key': new_status,
        'note': note,
        'status_url': status_url,
    }
    email = application.applicant.user.email
    return _send(subject, email, 'admissions/emails/status_change.html', context)


def send_action_required_email(application, feedback):
    """Notify parent that documents need correction."""
    resubmit_url = f'{ADMISSION_SUBDOMAIN}/application/{application.application_number}/resubmit/'
    subject = f'Action Required: Documents Need Attention — {application.application_number}'
    context = {
        'application': application,
        'student_name': application.student_name,
        'feedback': feedback,
        'resubmit_url': resubmit_url,
        'deadline': application.resubmission_deadline,
        'flagged_docs': application.documents.filter(status='flagged'),
    }
    email = application.applicant.user.email
    return _send(subject, email, 'admissions/emails/action_required.html', context)


def send_offer_letter_email(application, pdf_bytes=None):
    """Send admission offer letter, optionally with PDF attachment."""
    accept_url = f'{ADMISSION_SUBDOMAIN}/application/{application.application_number}/accept-offer/'
    subject = f'Admission Offer — {application.application_number} — Janan Luwum Memorial SSS'
    context = {
        'application': application,
        'student_name': application.student_name,
        'accept_url': accept_url,
    }
    attachment = None
    if pdf_bytes:
        attachment = (
            f'Offer_Letter_{application.application_number}.pdf',
            pdf_bytes,
            'application/pdf',
        )
    email = application.applicant.user.email
    return _send(subject, email, 'admissions/emails/offer_letter.html', context, attachment=attachment)


def send_rejection_email(application, reason=''):
    """Notify applicant of rejection."""
    subject = f'Application Decision — {application.application_number}'
    context = {
        'application': application,
        'student_name': application.student_name,
        'reason': reason,
    }
    email = application.applicant.user.email
    return _send(subject, email, 'admissions/emails/rejection.html', context)


# ============================================================================
# BULK EMAIL
# ============================================================================

def send_bulk_email(applications_qs, subject, message_body, staff_user=None):
    """Send the same message to multiple applicants. Returns (success_count, fail_count)."""
    success, fail = 0, 0
    for app in applications_qs.select_related('applicant__user', 'student'):
        try:
            context = {
                'application': app,
                'student_name': app.student_name,
                'message_body': message_body,
                'status_url': f'{ADMISSION_SUBDOMAIN}/application/{app.application_number}/status/',
            }
            sent = _send(subject, app.applicant.user.email, 'admissions/emails/bulk_message.html', context)
            if sent:
                success += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    return success, fail
