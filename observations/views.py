from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SiteHome(LoginRequiredMixin, TemplateView):
    """Static template view for the site homepage.
    """
    template_name = 'observations/site_home.html'

    def get_context_data(self, **kwargs):
        context = super(SiteHome, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['superuser'] = True
        context['page_title'] = settings.SITE_ACRONYM
        context['title'] = 'HOME'
        return context


class HelpPage(LoginRequiredMixin, TemplateView):
    """Help page (static template view).
    """
    template_name = "observations/help_page.html"
