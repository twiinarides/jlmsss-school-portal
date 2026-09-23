"""
Subdomain routing middleware for JLMSSS Admissions Portal.
Routes the admission subdomain to admissions.urls while keeping
the main website and Django admin on the main URL configuration.
"""

from django.conf import settings


ADMISSION_SUBDOMAIN = getattr(
    settings,
    "ADMISSION_SUBDOMAIN_HOST",
    "admission.jananluwummemorialsss.sc.ug",
)


class AdmissionSubdomainMiddleware:
    """
    Routes only the configured admission hostname to admissions.urls.

    Main domain:
        jananluwummemorialsss.sc.ug
        www.jananluwummemorialsss.sc.ug
        127.0.0.1
        localhost

    Admission domain:
        admission.jananluwummemorialsss.sc.ug
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()

        request.is_admission_portal = (
            host == ADMISSION_SUBDOMAIN.lower()
        )

        if request.is_admission_portal:
            request.urlconf = "admissions.urls"

        return self.get_response(request)
