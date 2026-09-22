"""
admissions/context_processors.py

Injects admission-related language and translation context into every template
rendered while the request is within the admissions portal.
"""

from .translations import TRANSLATIONS


def admission_context(request):
    """
    Context processor that exposes:
      - admission_lang  : the active language code ('en', 'lg', or 'rk')
      - admission_trans : the full translation dict for the active language
    """
    lang = request.session.get('admission_lang', 'en')

    # Validate — fall back to English for unrecognised codes
    if lang not in ('en', 'lg', 'rk'):
        lang = 'en'

    trans = TRANSLATIONS.get(lang, TRANSLATIONS['en'])

    return {
        'admission_lang': lang,
        'admission_trans': trans,
    }
