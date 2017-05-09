from __future__ import absolute_import

from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.http import HttpResponse
from django.utils.functional import curry
from django.views.generic import View, TemplateView

from flatpages_x.models import Revision
from flatpages_x.settings import PARSER
from flatpages_x.utils import load_path_attr

from .models import Video


class VideoImport(View):
    '''Basic view to import all outstanding encoded.
    View is intended to be accessed locally using curl during cron tasks.
    '''
    def get(self, request, *args, **kwargs):
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
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email)
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        return HttpResponse(
            '{} videos have been successfully imported.'.format(count))


class S3View(TemplateView):
    template_name = 's3_view.html'

    def get_context_data(self, **kwargs):
        context = super(S3View, self).get_context_data(**kwargs)

        if self.request.POST.get('limit'):
            limit = int(self.request.POST.get('limit'))
        else:
            limit = 0

        folder = "beach_return_cams_2"
        VIDEO_FORMATS = ('.mp4', '.avi', '.mkv')
        videos = [
            v for v in default_storage.listdir(folder)[1] if v.endswith(VIDEO_FORMATS)]
        vlist = []
        unimported = []
        for video in videos:
            item = {}
            imported = True if Video.objects.filter(
                file__icontains=video) else False
            item['video'] = video
            item['imported'] = imported
            vlist.append(item)

            if not imported:
                unimported.append(video)

        context['title'] = 'S3 Amazon - Beach Return Cams View'
        context['videos'] = videos
        context['video_list'] = vlist[:limit] if limit else vlist
        context['unimported_videos'] = unimported
        return context


@receiver(post_init, sender=FlatPage)
def FlatPageInterceptor(sender, instance, **kwargs):
    '''Amazon S3 expires its content on a fairly short turn-around. This means that its somewhat
    incompatible with html caching. This function, unfortunate as it is, intercepts the cache loads
    and regenerates it. It assumes html help pages are a minescule impact on the database in the scheme of things
    and only adds two SQL queries to the load. The code is largely copied from flatpages_x hence the
    possibly extraneous use of function currying
    '''
    sourcePage = Revision.objects.filter(
        flatpage=instance).order_by('-updated').first()
    render_func = curry(load_path_attr(PARSER[0], **PARSER[1]))
    instance.content = render_func(sourcePage.content_source)
    instance.save()
