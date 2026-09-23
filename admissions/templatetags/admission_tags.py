"""
admissions/templatetags/admission_tags.py

Custom template tags and filters for the JLMSSS admissions portal.

Usage in templates:
    {% load admission_tags %}

Available tags/filters:
    {% field_label field lang %}      - Multilingual field label
    {% field_help field lang %}       - Multilingual help text
    {% option_label option lang %}    - Multilingual option label
    {% section_title section lang %}  - Multilingual section title
    {{ status | status_badge }}       - Bootstrap badge HTML span
    {{ trans_dict | trans_key:key }}  - Safe dict lookup
    {% get_response application field_key %}  - Retrieve saved response text
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Multilingual label / help tags
# ---------------------------------------------------------------------------

@register.simple_tag
def field_label(field, lang='en'):
    """
    Return the label of a FormField in the requested language.
    Falls back to English if the translation is empty.

    Example::
        {% field_label field admission_lang %}
    """
    if lang == 'lg' and getattr(field, 'label_luganda', ''):
        return field.label_luganda
    if lang == 'rk' and getattr(field, 'label_runyakore', ''):
        return field.label_runyakore
    return field.label


@register.simple_tag
def field_help(field, lang='en'):
    """
    Return the help text of a FormField in the requested language.
    Falls back to English if the translation is empty.

    Example::
        {% field_help field admission_lang %}
    """
    if lang == 'lg' and getattr(field, 'help_text_luganda', ''):
        return field.help_text_luganda
    if lang == 'rk' and getattr(field, 'help_text_runyakore', ''):
        return field.help_text_runyakore
    return getattr(field, 'help_text', '')


@register.simple_tag
def option_label(option, lang='en'):
    """
    Return the label of a FieldOption in the requested language.
    Falls back to English if the translation is empty.

    Example::
        {% option_label option admission_lang %}
    """
    if lang == 'lg' and getattr(option, 'label_luganda', ''):
        return option.label_luganda
    if lang == 'rk' and getattr(option, 'label_runyakore', ''):
        return option.label_runyakore
    return option.label


@register.simple_tag
def section_title(section, lang='en'):
    """
    Return the title of a FormSection in the requested language.
    Falls back to English if the translation is empty.

    Example::
        {% section_title section admission_lang %}
    """
    if lang == 'lg' and getattr(section, 'title_luganda', ''):
        return section.title_luganda
    if lang == 'rk' and getattr(section, 'title_runyakore', ''):
        return section.title_runyakore
    return section.title


# ---------------------------------------------------------------------------
# Status badge filter
# ---------------------------------------------------------------------------

@register.filter(name='status_badge')
def status_badge(status):
    """
    Render a Bootstrap 5 badge <span> coloured according to the application status.

    Example::
        {{ application.status | status_badge }}
    """
    from admissions.utils import get_status_badge
    color = get_status_badge(status)
    label = status.replace('_', ' ').title()
    return mark_safe(f'<span class="badge bg-{color} text-white">{label}</span>')


# ---------------------------------------------------------------------------
# Translation dict lookup filter
# ---------------------------------------------------------------------------

@register.filter(name='trans_key')
def trans_key(trans_dict, key):
    """
    Safe dictionary lookup with key as the filter argument.
    Returns the key itself if not found (prevents silent empty output).

    Example::
        {{ admission_trans | trans_key:'apply_now' }}
    """
    if not isinstance(trans_dict, dict):
        return key
    return trans_dict.get(key, key)


# ---------------------------------------------------------------------------
# Application response retrieval tag
# ---------------------------------------------------------------------------

@register.simple_tag
def get_response(application, field_key):
    """
    Return the saved text value for a given field_key on an application.
    Returns an empty string if no response has been saved yet.

    Example::
        {% get_response application 'student_name' %}
    """
    try:
        resp = application.responses.filter(field_key=field_key).first()
        return resp.text_value if resp else ''
    except Exception:
        return ''


# ---------------------------------------------------------------------------
# Extra convenience tags
# ---------------------------------------------------------------------------

@register.simple_tag
def spots_display(window_entry_class, trans_dict):
    """
    Return a human-readable spots-remaining string using the provided
    translation dict.

    Example::
        {% spots_display entry_class admission_trans %}
    """
    remaining = window_entry_class.spots_remaining
    if remaining is None:
        return trans_dict.get('seats_available', 'Seats Available')
    if remaining == 0:
        return trans_dict.get('no_seats', 'No seats available')
    return f"{remaining} {trans_dict.get('seats_available', 'seat(s) available')}"


@register.filter(name='dict_get')
def dict_get(d, key):
    """
    Generic dictionary get filter.

    Example::
        {{ my_dict | dict_get:key }}
    """
    if isinstance(d, dict):
        return d.get(key, '')
    return ''
