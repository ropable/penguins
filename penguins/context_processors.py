from django.conf import settings


def template_context(request):
    """Pass extra context variables to every template.
    """
    context = {
        'application_version_no': settings.APPLICATION_VERSION_NO,
    }
    context.update(settings.STATIC_CONTEXT_VARS)
    return context
