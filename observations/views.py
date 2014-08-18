from __future__ import absolute_import

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View
    
from django.contrib.flatpages.models import FlatPage

from flatpages_x.models import Revision

from django.db.models.signals import post_init,pre_init
from django.dispatch import receiver

from .models import Video

from django.utils.functional import curry
from flatpages_x.settings import PARSER
from flatpages_x.utils import load_path_attr


class VideoImport(View):
    '''
    Basic view to import all outstanding encoded.
    View is intended to be accessed locally using curl during cron tasks.
    '''
    def get(self, request, *args, **kwargs):
        # Only allow requests to this view from localhost.
        #if request.META['SERVER_NAME'].lower() != 'localhost':
        #    return HttpResponseForbidden()
        # Localhost - proceed.
        v = Video.objects.all()[0]  # Get any random video object.
        count = v.import_folder()
        # Email each of the admin users the result of the import.
        subject = '[Penguins] Observations video import'
        from_email = 'penguins-alerts@dpaw.wa.gov.au'
        to_email = list(settings.ADMINS)
        text_content = '''This is an automated message to inform you that {}
            videos have been successfully imported by the Penguins Observations
            application.\nThis is an automatically-generated email - please do
            not reply.\n'''.format(count)
        html_content = '''This is an automated message to inform you that {}
            videos have been successfully imported by the Penguins Observations
            application.<br>This is an automatically-generated email - please do
            not reply.<br>'''.format(count)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return HttpResponse('{} videos have been successfully imported.'.format(count))


@receiver(post_init,sender=FlatPage)
def FlatPageInterceptor(sender, instance,  **kwargs):

    sourcePage = Revision.objects.filter(flatpage=instance).order_by('-updated').first()
    render_func = curry(load_path_attr(PARSER[0], **PARSER[1]))
    instance.content =  render_func(sourcePage.content_source)
    instance.save()


