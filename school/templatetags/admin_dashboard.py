from __future__ import annotations

from django import template
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

from school.models import ContactMessage, Event, Gallery, News, Staff

register = template.Library()


@register.simple_tag
def admin_kpis():
    return {
        "total_staff": Staff.objects.count(),
        "total_news": News.objects.count(),
        "total_events": Event.objects.count(),
        "total_gallery": Gallery.objects.count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
    }


@register.simple_tag
def admin_recent_activity(limit: int = 10):
    entries = (
        LogEntry.objects.select_related("content_type", "user")
        .order_by("-action_time")[:limit]
    )

    def _label(e: LogEntry) -> str:
        if not e.content_type_id:
            return ""
        ct: ContentType = e.content_type
        return f"{ct.app_label}.{ct.model}"

    return [
        {
            "action_time": e.action_time,
            "user": getattr(e.user, "username", ""),
            "object_repr": e.object_repr,
            "action_flag": e.action_flag,
            "message": e.get_change_message(),
            "model": _label(e),
        }
        for e in entries
    ]
