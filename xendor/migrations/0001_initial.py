# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Page'
        db.create_table(u'xendor_page', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['xendor.Page'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('menu_title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('content', self.gf('tinymce.models.HTMLField')(null=True, blank=True)),
            ('visible', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_menu', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_main', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('app_extension', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('menu_url', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('meta_title', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('meta_description', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('meta_keywords', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('parameters', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'xendor', ['Page'])

        # Adding model 'Fragment'
        db.create_table(u'xendor_fragment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('is_html', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'xendor', ['Fragment'])

        # Adding model 'Setting'
        db.create_table(u'xendor_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=2000)),
        ))
        db.send_create_signal(u'xendor', ['Setting'])


    def backwards(self, orm):
        # Deleting model 'Page'
        db.delete_table(u'xendor_page')

        # Deleting model 'Fragment'
        db.delete_table(u'xendor_fragment')

        # Deleting model 'Setting'
        db.delete_table(u'xendor_setting')


    models = {
        u'xendor.fragment': {
            'Meta': {'object_name': 'Fragment'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_html': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'xendor.page': {
            'Meta': {'object_name': 'Page'},
            'app_extension': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'content': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_menu': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'menu_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'menu_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'meta_description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'meta_keywords': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'meta_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'parameters': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['xendor.Page']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'xendor.setting': {
            'Meta': {'object_name': 'Setting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        }
    }

    complete_apps = ['xendor']