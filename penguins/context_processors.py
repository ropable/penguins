from django.conf import settings


def from_settings(request):
    """Dictionary of context variables to pass with every request response.
    """
    return {
        'application_version_no': settings.APPLICATION_VERSION_NO,
    }
