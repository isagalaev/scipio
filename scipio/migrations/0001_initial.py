# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Profile'
        db.create_table('scipio_profile', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='scipio_profile', unique=True, primary_key=True, to=orm['auth.User'])),
            ('openid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('openid_server', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('autoupdate', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('spamer', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('scipio', ['Profile'])

        # Adding model 'WhitelistSource'
        db.create_table('scipio_whitelistsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('scipio', ['WhitelistSource'])

        # Adding model 'CleanOpenID'
        db.create_table('scipio_cleanopenid', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('openid', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['scipio.WhitelistSource'])),
        ))
        db.send_create_signal('scipio', ['CleanOpenID'])

        # Adding unique constraint on 'CleanOpenID', fields ['openid', 'source']
        db.create_unique('scipio_cleanopenid', ['openid', 'source_id'])

    def backwards(self, orm):
        # Removing unique constraint on 'CleanOpenID', fields ['openid', 'source']
        db.delete_unique('scipio_cleanopenid', ['openid', 'source_id'])

        # Deleting model 'Profile'
        db.delete_table('scipio_profile')

        # Deleting model 'WhitelistSource'
        db.delete_table('scipio_whitelistsource')

        # Deleting model 'CleanOpenID'
        db.delete_table('scipio_cleanopenid')

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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 5, 21, 9, 744072)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 12, 14, 5, 21, 9, 743942)'}),
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
        'scipio.cleanopenid': {
            'Meta': {'ordering': "['openid']", 'unique_together': "[('openid', 'source')]", 'object_name': 'CleanOpenID'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'openid': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['scipio.WhitelistSource']"})
        },
        'scipio.profile': {
            'Meta': {'object_name': 'Profile'},
            'autoupdate': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'openid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'openid_server': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'spamer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'scipio_profile'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['auth.User']"})
        },
        'scipio.whitelistsource': {
            'Meta': {'object_name': 'WhitelistSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['scipio']