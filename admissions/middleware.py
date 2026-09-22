"""
admissions/middleware.py — Subdomain routing middleware for JLMSSS Admissions Portal.
Adds `request.is_admission_portal` flag based on the incoming Host header.
"""

from django.conf import settings

ADMISSION_SUBDOMAIN = getattr(settings, 'ADMISSION_SUBDOMAIN_HOST', 'admission.jananluwummemorialsss.sc.ug')


class AdmissionSubdomainMiddleware:
    """
    Sets request.is_admission_portal = True when the request arrives on the
    admission subdomain. Views and templates can check this flag.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        # Allow 127.0.0.1 for local testing of the admission portal
        request.is_admission_portal = (host == ADMISSION_SUBDOMAIN.lower() or host == '127.0.0.1')
        if request.is_admission_portal:
            request.urlconf = 'admissions.urls'
        response = self.get_response(request)
        return response
