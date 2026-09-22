"""
helpdesk/views.py

Views for the Janun Luwum Secondary School live helpdesk.

Public (AJAX) endpoints — no authentication required:
    start_session        POST  /help/start/
    send_message         POST  /help/send/
    get_messages         GET   /help/messages/<session_key>/

Staff-only endpoints — requires is_staff:
    admin_sessions       GET   /help/admin-desk/
    admin_session_detail GET+POST /help/admin-desk/<session_id>/
    close_session        POST  /help/admin-desk/<session_id>/close/
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from .models import HelpSession, HelpMessage


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _json_error(message: str, status: int = 400) -> JsonResponse:
    """Return a standardised JSON error response."""
    return JsonResponse({'success': False, 'error': message}, status=status)


def _parse_json_body(request) -> tuple[dict, str | None]:
    """
    Attempt to parse the request body as JSON.

    Returns (data_dict, error_string).  If parsing succeeds, error is None.
    """
    try:
        data = json.loads(request.body)
        return data, None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return {}, str(exc)


# --------------------------------------------------------------------------- #
# Public AJAX views
# --------------------------------------------------------------------------- #

@csrf_exempt
@require_POST
def start_session(request):
    """
    POST /help/start/

    Create or retrieve a HelpSession identified by the visitor's
    browser-generated UUID (session_key).

    Expected JSON body:
        {
            "session_key": "<uuid>",
            "name":        "Visitor Full Name",
            "email":       "visitor@example.com",
            "phone":       "+256 700 123456",   // optional
            "subject":     "School fees query"  // optional
        }

    Response JSON:
        {
            "success":    true,
            "session_id": 42,
            "session_key": "<uuid>"
        }
    """
    data, parse_error = _parse_json_body(request)
    if parse_error:
        return _json_error(f'Invalid JSON: {parse_error}')

    session_key = data.get('session_key', '').strip()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', '').strip()

    # Basic validation
    if not session_key:
        return _json_error('session_key is required.')
    if not name:
        return _json_error('name is required.')
    if not email:
        return _json_error('email is required.')

    session, created = HelpSession.objects.get_or_create(
        session_key=session_key,
        defaults={
            'visitor_name': name,
            'visitor_email': email,
            'visitor_phone': phone,
            'subject': subject,
        },
    )

    # If the session is new or has no messages yet, pre-populate the System Assistant prompt
    if created or session.messages.count() == 0:
        from .models import HelpMessage
        HelpMessage.objects.create(
            session=session,
            sender_type='admin',
            sender_name='System Assistant',
            message='We shall call you soon on the contacts provided either by email or direct calls in case the help desk delays to respond here.'
        )

    # If the session already existed, update contact details in case they
    # changed (e.g. visitor reloads the page and re-submits the form).
    if not created:
        updated_fields = []
        if name and session.visitor_name != name:
            session.visitor_name = name
            updated_fields.append('visitor_name')
        if email and session.visitor_email != email:
            session.visitor_email = email
            updated_fields.append('visitor_email')
        if phone and session.visitor_phone != phone:
            session.visitor_phone = phone
            updated_fields.append('visitor_phone')
        if subject and not session.subject:
            session.subject = subject
            updated_fields.append('subject')
        if updated_fields:
            session.save(update_fields=updated_fields)

    return JsonResponse({
        'success': True,
        'session_id': session.pk,
        'session_key': session.session_key,
    })


@csrf_exempt
@require_POST
def visitor_close_session(request):
    """
    POST /help/close/

    Allow a visitor to end / close / terminate their conversation.
    """
    data, parse_error = _parse_json_body(request)
    if parse_error:
        return _json_error(f'Invalid JSON: {parse_error}')

    session_key = data.get('session_key', '').strip()
    if not session_key:
        return _json_error('session_key is required.')

    try:
        session = HelpSession.objects.get(session_key=session_key)
        session.status = 'resolved'
        session.resolved_at = timezone.now()
        session.save(update_fields=['status', 'resolved_at'])
        return JsonResponse({'success': True})
    except HelpSession.DoesNotExist:
        return _json_error('Session not found.', status=404)


@csrf_exempt
@require_POST
def send_message(request):
    """
    POST /help/send/

    Create a new HelpMessage within an existing HelpSession.

    Expected JSON body:
        {
            "session_key":  "<uuid>",
            "message":      "Hello, I need help with ...",
            "sender_type":  "visitor"  // "visitor" (default) or "admin"
        }

    Response JSON:
        {
            "success":    true,
            "message_id": 17,
            "sent_at":    "2026-07-09T20:45:00Z"
        }
    """
    data, parse_error = _parse_json_body(request)
    if parse_error:
        return _json_error(f'Invalid JSON: {parse_error}')

    session_key = data.get('session_key', '').strip()
    message_text = data.get('message', '').strip()
    sender_type = data.get('sender_type', 'visitor').strip()

    # Validation
    if not session_key:
        return _json_error('session_key is required.')
    if not message_text:
        return _json_error('message is required.')
    if sender_type not in ('visitor', 'admin'):
        return _json_error('sender_type must be "visitor" or "admin".')

    try:
        session = HelpSession.objects.get(session_key=session_key)
    except HelpSession.DoesNotExist:
        return _json_error('Session not found.', status=404)

    # Determine sender display name
    if sender_type == 'admin' and request.user.is_authenticated and request.user.is_staff:
        sender_name = request.user.get_full_name() or request.user.username
    else:
        sender_name = session.visitor_name

    help_message = HelpMessage.objects.create(
        session=session,
        sender_type=sender_type,
        sender_name=sender_name,
        message=message_text,
    )

    # Update session status based on who just sent a message
    if sender_type == 'visitor':
        if session.status != 'open':
            session.status = 'visitor_replied'
    else:
        session.status = 'admin_replied'
    session.save()  # triggers auto_now on last_activity_at

    return JsonResponse({
        'success': True,
        'message_id': help_message.pk,
        'sent_at': help_message.sent_at.isoformat(),
    })


@require_GET
def get_messages(request, session_key: str):
    """
    GET /help/messages/<session_key>/

    Return messages for a session, optionally filtered to only those
    newer than a given message ID (for polling).

    Query parameters:
        last_id (int, optional) – Only return messages with id > last_id.

    Side effect:
        Admin messages are marked as is_read=True (visitor has now seen them).

    Response JSON:
        [
            {
                "id":          17,
                "sender_type": "admin",
                "sender_name": "Mr. Opiyo",
                "message":     "Hello, how can I help?",
                "sent_at":     "2026-07-09T20:45:00Z",
                "is_read":     true
            },
            ...
        ]
    """
    try:
        session = HelpSession.objects.get(session_key=session_key)
    except HelpSession.DoesNotExist:
        return _json_error('Session not found.', status=404)

    qs = session.messages.all()

    # Filter to only new messages if last_id is provided
    last_id_param = request.GET.get('last_id')
    if last_id_param:
        try:
            last_id = int(last_id_param)
            qs = qs.filter(pk__gt=last_id)
        except ValueError:
            return _json_error('last_id must be an integer.')

    # Mark admin messages as read by the visitor
    unread_admin_ids = list(
        qs.filter(sender_type='admin', is_read=False).values_list('pk', flat=True)
    )
    if unread_admin_ids:
        HelpMessage.objects.filter(pk__in=unread_admin_ids).update(is_read=True)

    payload = [
        {
            'id': msg.pk,
            'sender_type': msg.sender_type,
            'sender_name': msg.sender_name,
            'message': msg.message,
            'sent_at': msg.sent_at.isoformat(),
            'is_read': msg.is_read,
        }
        for msg in qs
    ]

    return JsonResponse({
        'messages': payload,
        'session_status': session.status,
    })


# --------------------------------------------------------------------------- #
# Staff-only views
# --------------------------------------------------------------------------- #

@staff_member_required(login_url='/admin/login/')
def admin_sessions(request):
    """
    GET /help/admin-desk/

    Dashboard listing all HelpSessions for staff members.
    Paginated at 20 sessions per page.

    Context:
        sessions      – Page object of HelpSession instances.
        open_count    – Count of sessions with status='open'.
        total_unread  – Total unread visitor messages across all sessions.
    """
    all_sessions = (
        HelpSession.objects
        .prefetch_related('messages')
        .order_by('-last_activity_at')
    )

    # Aggregate counts
    open_count = all_sessions.filter(status__in=['open', 'visitor_replied']).count()
    total_unread = sum(s.unread_by_admin for s in all_sessions)

    # Pagination
    paginator = Paginator(all_sessions, 20)
    page_number = request.GET.get('page')
    try:
        sessions_page = paginator.page(page_number)
    except PageNotAnInteger:
        sessions_page = paginator.page(1)
    except EmptyPage:
        sessions_page = paginator.page(paginator.num_pages)

    context = {
        'sessions': sessions_page,
        'open_count': open_count,
        'total_unread': total_unread,
    }
    return render(request, 'helpdesk/admin_sessions.html', context)


@staff_member_required(login_url='/admin/login/')
def admin_session_detail(request, session_id: int):
    """
    GET/POST /help/admin-desk/<session_id>/

    Staff view for reading and replying to a single HelpSession.

    GET:
        Displays the full conversation history.

    POST (admin reply):
        Form fields:
            reply_message – Text of the admin's reply.
        Side effects:
            - Creates a HelpMessage with sender_type='admin'.
            - Marks all visitor messages in this session as is_read=True.
            - Updates session.status to 'admin_replied'.
        Redirects back to the same page on success.

    Context:
        session        – The HelpSession instance.
        messages_list  – All HelpMessage instances for the session.
    """
    session = get_object_or_404(
        HelpSession.objects.prefetch_related('messages__session'),
        pk=session_id,
    )

    if request.method == 'POST':
        reply_text = (request.POST.get('reply_message') or request.POST.get('message') or '').strip()

        if not reply_text:
            messages.error(request, 'Reply message cannot be empty.')
            return redirect('helpdesk:helpdesk_admin_detail', session_id=session_id)

        # Create the admin reply message
        HelpMessage.objects.create(
            session=session,
            sender_type='admin',
            sender_name=request.user.get_full_name() or request.user.username,
            message=reply_text,
            is_read=False,
        )

        # Mark all visitor messages in this session as read
        session.messages.filter(sender_type='visitor', is_read=False).update(is_read=True)

        # Update session status
        session.status = 'admin_replied'
        session.save()

        messages.success(request, 'Reply sent successfully.')
        return redirect('helpdesk:helpdesk_admin_detail', session_id=session_id)

    # GET: mark unread visitor messages as read now that admin is viewing
    session.messages.filter(sender_type='visitor', is_read=False).update(is_read=True)

    messages_list = session.messages.order_by('sent_at')

    # Fetch all sessions for the sidebar list so admin can choose what to reply
    all_sessions = (
        HelpSession.objects
        .prefetch_related('messages')
        .order_by('-last_activity_at')
    )
    open_count = all_sessions.filter(status__in=['open', 'visitor_replied']).count()
    total_unread = sum(s.unread_by_admin for s in all_sessions)

    # Sidebar pagination or top list
    paginator = Paginator(all_sessions, 30)  # Show top 30 sessions in detail view sidebar
    page_number = request.GET.get('page')
    try:
        sessions_page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        sessions_page = paginator.page(1)

    context = {
        'session': session,
        'messages_list': messages_list,
        'sessions': sessions_page,
        'open_count': open_count,
        'total_unread': total_unread,
    }
    return render(request, 'helpdesk/admin_session_detail.html', context)


@staff_member_required(login_url='/admin/login/')
@require_POST
def close_session(request, session_id: int):
    """
    POST /help/admin-desk/<session_id>/close/

    Mark a HelpSession as resolved, recording who closed it and when.
    Redirects to the admin sessions list after closing.
    """
    session = get_object_or_404(HelpSession, pk=session_id)

    if session.status != 'resolved':
        session.status = 'resolved'
        session.resolved_at = timezone.now()
        session.resolved_by = request.user
        session.save(update_fields=['status', 'resolved_at', 'resolved_by'])
        messages.success(
            request,
            f'Session for {session.visitor_name} has been marked as resolved.',
        )
    else:
        messages.info(request, 'This session was already resolved.')

    return redirect('helpdesk:helpdesk_admin_sessions')
