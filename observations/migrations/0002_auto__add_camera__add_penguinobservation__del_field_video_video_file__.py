# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Camera'
        db.create_table(u'observations_camera', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('location', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'observations', ['Camera'])

        # Adding model 'PenguinObservation'
        db.create_table(u'observations_penguinobservation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['observations.Video'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'observations', ['PenguinObservation'])

        # Deleting field 'Video.video_file'
        db.delete_column(u'observations_video', 'video_file')

        # Deleting field 'Video.video_title'
        db.delete_column(u'observations_video', 'video_title')

        # Adding field 'Video.name'
        db.add_column(u'observations_video', 'name',
                      self.gf('django.db.models.fields.CharField')(default='test', max_length=100),
                      keep_default=False)

        # Adding field 'Video.camera'
        db.add_column(u'observations_video', 'camera',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['observations.Camera']),
                      keep_default=False)

        # Adding field 'Video.file'
        db.add_column(u'observations_video', 'file',
                      self.gf('django.db.models.fields.files.FileField')(default='videos/test.mov', max_length=100),
                      keep_default=False)

        # Adding field 'Video.start_time'
        db.add_column(u'observations_video', 'start_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 7, 0, 0)),
                      keep_default=False)

        # Adding field 'Video.end_time'
        db.add_column(u'observations_video', 'end_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 7, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Camera'
        db.delete_table(u'observations_camera')

        # Deleting model 'PenguinObservation'
        db.delete_table(u'observations_penguinobservation')


        # User chose to not deal with backwards NULL issues for 'Video.video_file'
        raise RuntimeError("Cannot reverse this migration. 'Video.video_file' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Video.video_file'
        db.add_column(u'observations_video', 'video_file',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Video.video_title'
        raise RuntimeError("Cannot reverse this migration. 'Video.video_title' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Video.video_title'
        db.add_column(u'observations_video', 'video_title',
                      self.gf('django.db.models.fields.TextField')(),
                      keep_default=False)

        # Deleting field 'Video.name'
        db.delete_column(u'observations_video', 'name')

        # Deleting field 'Video.camera'
        db.delete_column(u'observations_video', 'camera_id')

        # Deleting field 'Video.file'
        db.delete_column(u'observations_video', 'file')

        # Deleting field 'Video.start_time'
        db.delete_column(u'observations_video', 'start_time')

        # Deleting field 'Video.end_time'
        db.delete_column(u'observations_video', 'end_time')


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
            'ip_address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'observations.penguincount': {
            'Meta': {'object_name': 'PenguinCount'},
            'civil_twilight': ('django.db.models.fields.TimeField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'fifteen_to_thirty': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fourty_five_to_sixty': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ninety_to_one_oh_five': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'observer': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'one_oh_five_to_one_twenty': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'seventy_five_to_ninety': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sixty_to_seventy_five': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'sub_fifteen': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thirty_to_fourty_five': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_penguins': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'zero_to_fifteen': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'observations.penguinobservation': {
            'Meta': {'object_name': 'PenguinObservation'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Video']"})
        },
        u'observations.video': {
            'Meta': {'object_name': 'Video'},
            'camera': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['observations.Camera']"}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['observations']