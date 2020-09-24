from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from observations.models import Video


class Command(BaseCommand):
    help = 'Imports outstanding encoded videos'

    def handle(self, *args, **options):
        v = Video.objects.first()  # Get any random video object.
        count = v.import_folder()  # Do the import.
        # Email each of the admin users the results of the import.
        subject = '[Penguins] Observations video import'
        from_email = 'penguins-alerts@dbca.wa.gov.au'
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
        msg.send(fail_silently=True)
