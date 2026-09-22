"""
helpdesk/migrations/0001_initial.py

Initial migration for the helpdesk app.

Creates:
    helpdesk_helpsession  – Chat session initiated by a website visitor.
    helpdesk_helpmessage  – Individual message within a session.
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # HelpSession
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HelpSession',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'session_key',
                    models.CharField(
                        db_index=True,
                        help_text='Browser-generated UUID stored in visitor localStorage.',
                        max_length=128,
                        unique=True,
                    ),
                ),
                (
                    'visitor_name',
                    models.CharField(
                        help_text='Full name provided by the visitor.',
                        max_length=100,
                    ),
                ),
                (
                    'visitor_email',
                    models.EmailField(
                        help_text='Contact e-mail of the visitor.',
                        max_length=254,
                    ),
                ),
                (
                    'visitor_phone',
                    models.CharField(
                        blank=True,
                        help_text='Optional phone number of the visitor.',
                        max_length=20,
                    ),
                ),
                (
                    'subject',
                    models.CharField(
                        blank=True,
                        help_text='Brief subject / topic of the enquiry.',
                        max_length=200,
                    ),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('open', 'Open'),
                            ('admin_replied', 'Admin Replied'),
                            ('visitor_replied', 'Visitor Replied'),
                            ('resolved', 'Resolved'),
                        ],
                        db_index=True,
                        default='open',
                        max_length=20,
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    'last_activity_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text='Automatically updated whenever the session record is saved.',
                    ),
                ),
                (
                    'resolved_at',
                    models.DateTimeField(
                        blank=True,
                        help_text='Timestamp when the session was marked resolved.',
                        null=True,
                    ),
                ),
                (
                    'resolved_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='Staff member who resolved the session.',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='resolved_help_sessions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Help Session',
                'verbose_name_plural': 'Help Sessions',
                'ordering': ['-last_activity_at'],
            },
        ),

        # ------------------------------------------------------------------ #
        # HelpMessage
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name='HelpMessage',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'sender_type',
                    models.CharField(
                        choices=[
                            ('visitor', 'Visitor'),
                            ('admin', 'Admin'),
                        ],
                        help_text='Who sent this message.',
                        max_length=10,
                    ),
                ),
                (
                    'sender_name',
                    models.CharField(
                        blank=True,
                        help_text='Display name of the sender (auto-populated where available).',
                        max_length=100,
                    ),
                ),
                (
                    'message',
                    models.TextField(
                        help_text='Body text of the message.',
                    ),
                ),
                (
                    'is_read',
                    models.BooleanField(
                        default=False,
                        help_text=(
                            'For visitor messages: True once an admin has read it. '
                            'For admin messages: True once the visitor has seen it.'
                        ),
                    ),
                ),
                (
                    'sent_at',
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    'attachment',
                    models.FileField(
                        blank=True,
                        help_text='Optional file attachment.',
                        null=True,
                        upload_to='helpdesk/attachments/',
                    ),
                ),
                (
                    'session',
                    models.ForeignKey(
                        help_text='The help session this message belongs to.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='messages',
                        to='helpdesk.helpsession',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Help Message',
                'verbose_name_plural': 'Help Messages',
                'ordering': ['sent_at'],
            },
        ),
    ]
