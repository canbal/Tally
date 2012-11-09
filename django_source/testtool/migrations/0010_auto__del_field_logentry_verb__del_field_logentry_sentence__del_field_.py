# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'LogEntry.verb'
        db.delete_column('testtool_logentry', 'verb')

        # Deleting field 'LogEntry.sentence'
        db.delete_column('testtool_logentry', 'sentence')

        # Deleting field 'LogEntry.subject'
        db.delete_column('testtool_logentry', 'subject_id')

        # Adding field 'LogEntry.actor'
        db.add_column('testtool_logentry', 'actor',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='actor_logentries', to=orm['testtool.UserProfile']),
                      keep_default=False)

        # Adding field 'LogEntry.action'
        db.add_column('testtool_logentry', 'action',
                      self.gf('django.db.models.fields.CharField')(default='edited', max_length=20),
                      keep_default=False)

        # Adding field 'LogEntry.message'
        db.add_column('testtool_logentry', 'message',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Removing M2M table for field prep_objects on 'LogEntry'
        db.delete_table('testtool_logentry_prep_objects')

        # Adding M2M table for field tags on 'LogEntry'
        db.create_table('testtool_logentry_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('logentry', models.ForeignKey(orm['testtool.logentry'], null=False)),
            ('userprofile', models.ForeignKey(orm['testtool.userprofile'], null=False))
        ))
        db.create_unique('testtool_logentry_tags', ['logentry_id', 'userprofile_id'])


    def backwards(self, orm):
        # Adding field 'LogEntry.verb'
        db.add_column('testtool_logentry', 'verb',
                      self.gf('django.db.models.fields.CharField')(default='edited', max_length=20),
                      keep_default=False)

        # Adding field 'LogEntry.sentence'
        db.add_column('testtool_logentry', 'sentence',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'LogEntry.subject'
        db.add_column('testtool_logentry', 'subject',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='subject_logentries', to=orm['testtool.UserProfile']),
                      keep_default=False)

        # Deleting field 'LogEntry.actor'
        db.delete_column('testtool_logentry', 'actor_id')

        # Deleting field 'LogEntry.action'
        db.delete_column('testtool_logentry', 'action')

        # Deleting field 'LogEntry.message'
        db.delete_column('testtool_logentry', 'message')

        # Adding M2M table for field prep_objects on 'LogEntry'
        db.create_table('testtool_logentry_prep_objects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('logentry', models.ForeignKey(orm['testtool.logentry'], null=False)),
            ('userprofile', models.ForeignKey(orm['testtool.userprofile'], null=False))
        ))
        db.create_unique('testtool_logentry_prep_objects', ['logentry_id', 'userprofile_id'])

        # Removing M2M table for field tags on 'LogEntry'
        db.delete_table('testtool_logentry_tags')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'testtool.logentry': {
            'Meta': {'object_name': 'LogEntry'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor_logentries'", 'to': "orm['testtool.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'object': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'tags_logentries'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['testtool.UserProfile']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'testtool.scoredscqs': {
            'Meta': {'object_name': 'ScoreDSCQS'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.UserProfile']"}),
            'test_case_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestCaseInstance']"}),
            'value1': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'}),
            'value2': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '2'})
        },
        'testtool.scoredsis': {
            'Meta': {'object_name': 'ScoreDSIS'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.UserProfile']"}),
            'test_case_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestCaseInstance']"}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'testtool.scoresscqe': {
            'Meta': {'object_name': 'ScoreSSCQE'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.UserProfile']"}),
            'test_case_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestCaseInstance']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        'testtool.test': {
            'Meta': {'object_name': 'Test'},
            'collaborators': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'collaborators_tests'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['testtool.UserProfile']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "'DSIS'", 'max_length': '10'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner_tests'", 'to': "orm['testtool.UserProfile']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'testtool.testcase': {
            'Meta': {'object_name': 'TestCase'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.Test']"}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['testtool.Video']", 'through': "orm['testtool.TestCaseItem']", 'symmetrical': 'False'})
        },
        'testtool.testcaseinstance': {
            'Meta': {'unique_together': "(('test_instance', 'play_order'),)", 'object_name': 'TestCaseInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_media_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'play_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'test_case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestCase']"}),
            'test_instance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestInstance']"})
        },
        'testtool.testcaseitem': {
            'Meta': {'unique_together': "(('test_case', 'play_order'),)", 'object_name': 'TestCaseItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_reference': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'play_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'test_case': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.TestCase']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.Video']"})
        },
        'testtool.testinstance': {
            'Meta': {'object_name': 'TestInstance'},
            'collaborators': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'collaborators_testinstances'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['testtool.UserProfile']"}),
            'counter': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner_testinstances'", 'to': "orm['testtool.UserProfile']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'run_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'schedule_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'subjects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subjects_testinstances'", 'null': 'True', 'to': "orm['testtool.UserProfile']"}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.Test']"})
        },
        'testtool.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'birth_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'testtool.video': {
            'Meta': {'unique_together': "(('test', 'filename'),)", 'object_name': 'Video'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.Test']"})
        }
    }

    complete_apps = ['testtool']