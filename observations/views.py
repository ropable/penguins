from __future__ import absolute_import
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class HelpPage(LoginRequiredMixin, TemplateView):
    """Help page (static template view).
    """
    template_name = "help_page.html"
