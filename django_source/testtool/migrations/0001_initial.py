# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table('testtool_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('birth_date', self.gf('django.db.models.fields.DateField')()),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('testtool', ['UserProfile'])

        # Adding model 'Test'
        db.create_table('testtool_test', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner_tests', to=orm['testtool.UserProfile'])),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('method', self.gf('django.db.models.fields.CharField')(default='DSIS', max_length=10)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('testtool', ['Test'])

        # Adding M2M table for field collaborators on 'Test'
        db.create_table('testtool_test_collaborators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('test', models.ForeignKey(orm['testtool.test'], null=False)),
            ('userprofile', models.ForeignKey(orm['testtool.userprofile'], null=False))
        ))
        db.create_unique('testtool_test_collaborators', ['test_id', 'userprofile_id'])

        # Adding model 'TestInstance'
        db.create_table('testtool_testinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.Test'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner_testinstances', to=orm['testtool.UserProfile'])),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('schedule_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('run_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('counter', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal('testtool', ['TestInstance'])

        # Adding M2M table for field collaborators on 'TestInstance'
        db.create_table('testtool_testinstance_collaborators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testinstance', models.ForeignKey(orm['testtool.testinstance'], null=False)),
            ('userprofile', models.ForeignKey(orm['testtool.userprofile'], null=False))
        ))
        db.create_unique('testtool_testinstance_collaborators', ['testinstance_id', 'userprofile_id'])

        # Adding M2M table for field subjects on 'TestInstance'
        db.create_table('testtool_testinstance_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('testinstance', models.ForeignKey(orm['testtool.testinstance'], null=False)),
            ('userprofile', models.ForeignKey(orm['testtool.userprofile'], null=False))
        ))
        db.create_unique('testtool_testinstance_subjects', ['testinstance_id', 'userprofile_id'])

        # Adding model 'Video'
        db.create_table('testtool_video', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.Test'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=400, null=True, blank=True)),
        ))
        db.send_create_signal('testtool', ['Video'])

        # Adding unique constraint on 'Video', fields ['test', 'filename']
        db.create_unique('testtool_video', ['test_id', 'filename'])

        # Adding model 'TestCase'
        db.create_table('testtool_testcase', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.Test'])),
        ))
        db.send_create_signal('testtool', ['TestCase'])

        # Adding model 'TestCaseInstance'
        db.create_table('testtool_testcaseinstance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestInstance'])),
            ('test_case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestCase'])),
            ('is_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_media_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('play_order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('testtool', ['TestCaseInstance'])

        # Adding unique constraint on 'TestCaseInstance', fields ['test_instance', 'play_order']
        db.create_unique('testtool_testcaseinstance', ['test_instance_id', 'play_order'])

        # Adding model 'TestCaseItem'
        db.create_table('testtool_testcaseitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_case', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestCase'])),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.Video'])),
            ('play_order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_reference', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('testtool', ['TestCaseItem'])

        # Adding unique constraint on 'TestCaseItem', fields ['test_case', 'play_order']
        db.create_unique('testtool_testcaseitem', ['test_case_id', 'play_order'])

        # Adding model 'ScoreSSCQE'
        db.create_table('testtool_scoresscqe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_case_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestCaseInstance'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.UserProfile'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('testtool', ['ScoreSSCQE'])

        # Adding model 'ScoreDSIS'
        db.create_table('testtool_scoredsis', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_case_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestCaseInstance'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.UserProfile'])),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('testtool', ['ScoreDSIS'])

        # Adding model 'ScoreDSCQS'
        db.create_table('testtool_scoredscqs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test_case_instance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.TestCaseInstance'])),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['testtool.UserProfile'])),
            ('value1', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
            ('value2', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=2)),
        ))
        db.send_create_signal('testtool', ['ScoreDSCQS'])


    def backwards(self, orm):
        # Removing unique constraint on 'TestCaseItem', fields ['test_case', 'play_order']
        db.delete_unique('testtool_testcaseitem', ['test_case_id', 'play_order'])

        # Removing unique constraint on 'TestCaseInstance', fields ['test_instance', 'play_order']
        db.delete_unique('testtool_testcaseinstance', ['test_instance_id', 'play_order'])

        # Removing unique constraint on 'Video', fields ['test', 'filename']
        db.delete_unique('testtool_video', ['test_id', 'filename'])

        # Deleting model 'UserProfile'
        db.delete_table('testtool_userprofile')

        # Deleting model 'Test'
        db.delete_table('testtool_test')

        # Removing M2M table for field collaborators on 'Test'
        db.delete_table('testtool_test_collaborators')

        # Deleting model 'TestInstance'
        db.delete_table('testtool_testinstance')

        # Removing M2M table for field collaborators on 'TestInstance'
        db.delete_table('testtool_testinstance_collaborators')

        # Removing M2M table for field subjects on 'TestInstance'
        db.delete_table('testtool_testinstance_subjects')

        # Deleting model 'Video'
        db.delete_table('testtool_video')

        # Deleting model 'TestCase'
        db.delete_table('testtool_testcase')

        # Deleting model 'TestCaseInstance'
        db.delete_table('testtool_testcaseinstance')

        # Deleting model 'TestCaseItem'
        db.delete_table('testtool_testcaseitem')

        # Deleting model 'ScoreSSCQE'
        db.delete_table('testtool_scoresscqe')

        # Deleting model 'ScoreDSIS'
        db.delete_table('testtool_scoredsis')

        # Deleting model 'ScoreDSCQS'
        db.delete_table('testtool_scoredscqs')


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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['testtool.Test']"})
        }
    }

    complete_apps = ['testtool']