# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ObserverCounter'
        db.create_table(u'observations_observercounter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'observations', ['ObserverCounter'])

        # Adding field 'PenguinCount.outlier'
        #db.add_column(u'observations_penguincount', 'outlier',
        #              self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=5, decimal_places=2),
        #              keep_default=False)


        # Changing field 'PenguinCount.fourty_five_to_sixty'
        db.alter_column(u'observations_penguincount', 'fourty_five_to_sixty', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.seventy_five_to_ninety'
        db.alter_column(u'observations_penguincount', 'seventy_five_to_ninety', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.zero_to_fifteen'
        db.alter_column(u'observations_penguincount', 'zero_to_fifteen', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.sub_fifteen'
        db.alter_column(u'observations_penguincount', 'sub_fifteen', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.thirty_to_fourty_five'
        db.alter_column(u'observations_penguincount', 'thirty_to_fourty_five', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.sixty_to_seventy_five'
        db.alter_column(u'observations_penguincount', 'sixty_to_seventy_five', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.fifteen_to_thirty'
        db.alter_column(u'observations_penguincount', 'fifteen_to_thirty', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.ninety_to_one_oh_five'
        db.alter_column(u'observations_penguincount', 'ninety_to_one_oh_five', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.one_oh_five_to_one_twenty'
        db.alter_column(u'observations_penguincount', 'one_oh_five_to_one_twenty', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'PenguinCount.total_penguins'
        db.alter_column(u'observations_penguincount', 'total_penguins', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))
        # Adding field 'Video.views'
        db.add_column(u'observations_video', 'views',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ObserverCounter'
        db.delete_table(u'observations_observercounter')

        # Deleting field 'PenguinCount.outlier'
        db.delete_column(u'observations_penguincount', 'outlier')


        # Changing field 'PenguinCount.fourty_five_to_sixty'
        db.alter_column(u'observations_penguincount', 'fourty_five_to_sixty', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.seventy_five_to_ninety'
        db.alter_column(u'observations_penguincount', 'seventy_five_to_ninety', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.zero_to_fifteen'
        db.alter_column(u'observations_penguincount', 'zero_to_fifteen', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.sub_fifteen'
        db.alter_column(u'observations_penguincount', 'sub_fifteen', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.thirty_to_fourty_five'
        db.alter_column(u'observations_penguincount', 'thirty_to_fourty_five', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.sixty_to_seventy_five'
        db.alter_column(u'observations_penguincount', 'sixty_to_seventy_five', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.fifteen_to_thirty'
        db.alter_column(u'observations_penguincount', 'fifteen_to_thirty', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.ninety_to_one_oh_five'
        db.alter_column(u'observations_penguincount', 'ninety_to_one_oh_five', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.one_oh_five_to_one_twenty'
        db.alter_column(u'observations_penguincount', 'one_oh_five_to_one_twenty', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'PenguinCount.total_penguins'
        db.alter_column(u'observations_penguincount', 'total_penguins', self.gf('django.db.models.fields.IntegerField')())
        # Deleting field 'Video.views'
        db.delete_column(u'observations_video', 'views')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'observations.camera': {
            'Meta': {'object_name': 'Camera'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Site']", 'null': 'True', 'blank': 'True'})
        },
        u'observations.observercounter': {
            'Meta': {'object_name': 'ObserverCounter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'observations.penguincount': {
            'Meta': {'object_name': 'PenguinCount'},
            'civil_twilight': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'fifteen_to_thirty': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'fourty_five_to_sixty': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ninety_to_one_oh_five': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'one_oh_five_to_one_twenty': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'outlier': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'seventy_five_to_ninety': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Site']"}),
            'sixty_to_seventy_five': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'sub_fifteen': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'thirty_to_fourty_five': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'total_penguins': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'}),
            'zero_to_fifteen': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '2'})
        },
        u'observations.penguinobservation': {
            'Meta': {'object_name': 'PenguinObservation'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Camera']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'observer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'seen': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Site']"})
        },
        u'observations.penguinvideoobservation': {
            'Meta': {'object_name': 'PenguinVideoObservation'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Video']"})
        },
        u'observations.site': {
            'Meta': {'object_name': 'Site'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'observations.video': {
            'Meta': {'ordering': "[u'-date']", 'object_name': 'Video'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Camera']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_time': ('django.db.models.fields.TimeField', [], {}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['observations']
