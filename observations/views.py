from __future__ import absolute_import
from django.views.generic import TemplateView


class HelpPage(TemplateView):
    """Help page (static template view).
    """
    template_name = "help_page.html"
