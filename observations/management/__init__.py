from django.db.models.signals import post_syncdb
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import observations.models


@receiver(post_syncdb, sender=observations.models)
def add_view_permissions(sender, **kwargs):
    """
    This syncdb hook takes care of adding a view permission to all our
    content types.
    """
    for content_type in ContentType.objects.all():
        codename = "view_%s" % content_type.model
        if not Permission.objects.filter(content_type=content_type,
                                         codename=codename):
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name="Can view %s" % content_type.name)


@receiver(post_syncdb, sender=observations.models)
def add_default_group(sender, **kwargs):
    """
    Set up the default group and their permissions after syncdb.
    """
    group, created = Group.objects.get_or_create(name="Observers")

    permissions = (
        ('view_site', 'observations', 'site'),
        ('view_video', 'observations', 'video'),
        ('add_penguinobservation', 'observations', 'penguinobservation'),
        ('view_penguinobservation', 'observations', 'penguinobservation'),
    )

    for codename, app_label, model in permissions:
        permission = Permission.objects.get_by_natural_key(codename,
            app_label, model)
        group.permissions.add(permission)
