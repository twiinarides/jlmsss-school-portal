"""
helpdesk/admin.py

Jazzmin-compatible Django admin configuration for the helpdesk app.

Registers:
    HelpSession  – with inline messages, custom list columns, and bulk actions.
    HelpMessage  – standalone registration for direct message management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import HelpSession, HelpMessage


# --------------------------------------------------------------------------- #
# Inline
# --------------------------------------------------------------------------- #

class HelpMessageInline(admin.TabularInline):
    """
    Displays all messages for a session inline within HelpSessionAdmin.
    Admins cannot delete messages from this view to preserve audit trails.
    """

    model = HelpMessage
    fields = ['sender_type', 'sender_name', 'message', 'is_read', 'sent_at']
    readonly_fields = ['sent_at']
    extra = 0
    can_delete = False
    show_change_link = True
    classes = ['collapse']


# --------------------------------------------------------------------------- #
# HelpSession admin
# --------------------------------------------------------------------------- #

@admin.register(HelpSession)
class HelpSessionAdmin(admin.ModelAdmin):
    """
    Admin view for HelpSession.

    Provides a rich list view with unread-message counts, quick-reply links,
    filtering by status/date, full-text search, and a bulk 'mark resolved'
    action.
    """

    # ------------------------------------------------------------------ #
    # List view configuration
    # ------------------------------------------------------------------ #
    list_display = [
        'visitor_name',
        'visitor_email',
        'visitor_phone',
        'subject',
        'status',
        'unread_count',
        'last_activity_at',
        'reply_action',
    ]
    list_filter = ['status', 'created_at', 'last_activity_at']
    search_fields = ['visitor_name', 'visitor_email', 'subject']
    list_per_page = 25
    ordering = ['-last_activity_at']

    # ------------------------------------------------------------------ #
    # Detail view configuration
    # ------------------------------------------------------------------ #
    readonly_fields = [
        'session_key',
        'created_at',
        'last_activity_at',
        'resolved_at',
        'resolved_by',
    ]
    fieldsets = [
        (
            'Visitor Details',
            {
                'fields': (
                    'visitor_name',
                    'visitor_email',
                    'visitor_phone',
                    'session_key',
                )
            },
        ),
        (
            'Session Info',
            {
                'fields': (
                    'subject',
                    'status',
                    'created_at',
                    'last_activity_at',
                )
            },
        ),
        (
            'Resolution',
            {
                'fields': ('resolved_at', 'resolved_by'),
                'classes': ('collapse',),
            },
        ),
    ]
    inlines = [HelpMessageInline]
    actions = ['mark_resolved']

    # ------------------------------------------------------------------ #
    # Custom list columns
    # ------------------------------------------------------------------ #
    @admin.display(description='Unread')
    def unread_count(self, obj: HelpSession) -> int:
        """Returns the number of unread visitor messages for this session."""
        count = obj.unread_by_admin
        if count:
            return format_html(
                '<span style="'
                'background:#e74c3c;color:#fff;'
                'padding:2px 8px;border-radius:12px;font-weight:bold;">'
                '{}</span>',
                count,
            )
        return format_html(
            '<span style="color:#27ae60;font-weight:bold;">0</span>'
        )

    @admin.display(description='Reply')
    def reply_action(self, obj: HelpSession) -> str:
        """Renders a quick-reply button linking to the custom admin detail view."""
        return format_html(
            '<a href="{}" '
            'style="'
            'background:#3498db;color:#fff;'
            'padding:4px 10px;border-radius:4px;'
            'text-decoration:none;font-size:0.85em;">'
            '&#9993; Reply'
            '</a>',
            f'/help/admin-desk/{obj.pk}/',
        )

    # ------------------------------------------------------------------ #
    # Bulk actions
    # ------------------------------------------------------------------ #
    @admin.action(description='Mark selected sessions as resolved')
    def mark_resolved(self, request, queryset) -> None:
        """Bulk-mark selected HelpSessions as resolved."""
        updated = queryset.update(
            status='resolved',
            resolved_at=timezone.now(),
            resolved_by=request.user,
        )
        self.message_user(
            request,
            f'{updated} session(s) successfully marked as resolved.',
        )

    # ------------------------------------------------------------------ #
    # Queryset optimisation
    # ------------------------------------------------------------------ #
    def get_queryset(self, request):
        """Prefetch messages to avoid N+1 when computing unread counts."""
        qs = super().get_queryset(request)
        return qs.prefetch_related('messages')


# --------------------------------------------------------------------------- #
# HelpMessage standalone admin
# --------------------------------------------------------------------------- #

@admin.register(HelpMessage)
class HelpMessageAdmin(admin.ModelAdmin):
    """
    Standalone admin for individual HelpMessage records.

    Useful for moderation, auditing, or directly searching message content.
    """

    list_display = [
        'session',
        'sender_type',
        'sender_name',
        'short_message',
        'is_read',
        'sent_at',
    ]
    list_filter = ['sender_type', 'is_read', 'sent_at']
    search_fields = ['message', 'sender_name', 'session__visitor_name', 'session__visitor_email']
    readonly_fields = ['sent_at', 'session']
    ordering = ['-sent_at']
    list_per_page = 50

    @admin.display(description='Message Preview')
    def short_message(self, obj: HelpMessage) -> str:
        """Displays a truncated preview of the message body."""
        preview = obj.message[:80]
        if len(obj.message) > 80:
            preview += '…'
        return preview
