"""
helpdesk/models.py

Defines the data models for the Janun Luwum Secondary School live helpdesk.

Models:
    HelpSession  – One chat thread initiated by a website visitor.
    HelpMessage  – An individual message within a HelpSession.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class HelpSession(models.Model):
    """
    Represents a single support conversation started by a visitor.

    The session is keyed by a browser-generated UUID stored in the
    visitor's localStorage, so no login is required on the visitor side.
    """

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('admin_replied', 'Admin Replied'),
        ('visitor_replied', 'Visitor Replied'),
        ('resolved', 'Resolved'),
    ]

    # ------------------------------------------------------------------ #
    # Visitor identity
    # ------------------------------------------------------------------ #
    session_key = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
        help_text='Browser-generated UUID stored in visitor localStorage.',
    )
    visitor_name = models.CharField(
        max_length=100,
        help_text='Full name provided by the visitor.',
    )
    visitor_email = models.EmailField(
        help_text='Contact e-mail of the visitor.',
    )
    visitor_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Optional phone number of the visitor.',
    )

    # ------------------------------------------------------------------ #
    # Conversation metadata
    # ------------------------------------------------------------------ #
    subject = models.CharField(
        max_length=200,
        blank=True,
        help_text='Brief subject / topic of the enquiry.',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        db_index=True,
    )

    # ------------------------------------------------------------------ #
    # Timestamps
    # ------------------------------------------------------------------ #
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(
        auto_now=True,
        help_text='Automatically updated whenever the session record is saved.',
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the session was marked resolved.',
    )

    # ------------------------------------------------------------------ #
    # Resolution details
    # ------------------------------------------------------------------ #
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='resolved_help_sessions',
        help_text='Staff member who resolved the session.',
    )

    class Meta:
        ordering = ['-last_activity_at']
        verbose_name = 'Help Session'
        verbose_name_plural = 'Help Sessions'

    # ------------------------------------------------------------------ #
    # Properties
    # ------------------------------------------------------------------ #
    @property
    def unread_by_admin(self) -> int:
        """Number of visitor messages not yet read by admin staff."""
        return self.messages.filter(sender_type='visitor', is_read=False).count()

    @property
    def unread_by_visitor(self) -> int:
        """Number of admin messages not yet read by the visitor."""
        return self.messages.filter(sender_type='admin', is_read=False).count()

    def __str__(self) -> str:
        return f'{self.visitor_name} – {self.subject or "Help Request"}'


class HelpMessage(models.Model):
    """
    An individual message exchanged within a HelpSession.

    Messages can be sent by either the visitor or an admin staff member.
    Attachments are stored under MEDIA_ROOT/helpdesk/attachments/.
    """

    SENDER_CHOICES = [
        ('visitor', 'Visitor'),
        ('admin', 'Admin'),
    ]

    session = models.ForeignKey(
        HelpSession,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='The help session this message belongs to.',
    )
    sender_type = models.CharField(
        max_length=10,
        choices=SENDER_CHOICES,
        help_text='Who sent this message.',
    )
    sender_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Display name of the sender (auto-populated where available).',
    )
    message = models.TextField(
        help_text='Body text of the message.',
    )
    is_read = models.BooleanField(
        default=False,
        help_text=(
            'For visitor messages: True once an admin has read it. '
            'For admin messages: True once the visitor has seen it.'
        ),
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(
        upload_to='helpdesk/attachments/',
        null=True,
        blank=True,
        help_text='Optional file attachment.',
    )

    class Meta:
        ordering = ['sent_at']
        verbose_name = 'Help Message'
        verbose_name_plural = 'Help Messages'

    def __str__(self) -> str:
        return f'{self.sender_type}: {self.message[:50]}'
