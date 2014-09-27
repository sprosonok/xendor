# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf import settings

from xendor.forms import PageAdminForm
from xendor.models import Page, Fragment, Setting
from xendor.structure import Structure


class PageAdmin(admin.ModelAdmin):
    admin_label = u'Управление контентом'

    fieldsets = (
        ('', {
            'classes': ('closed',),
            'fields': ('title', 'menu_title', 'content', 'in_menu'),
        }),
        ('Метаданные', {
            'classes': ('grp-collapse grp-closed',),
            'description': 'Используются поисковиками для лучшей индексации страницы',
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
        }),
        ('Настройки', {
            'classes': ('grp-collapse grp-closed',),
            'description': 'Без четкой уверенности сюда лучше не лезть',
            'fields': ('slug', 'visible', 'parameters', 'template', 'app_extension', 'menu_url', 'is_main'),  # 'template',
        }),
        ('В структуре сайта..', {
            'classes': ('hidden',),
            'fields': ('parent',),
        })
    )

    list_display = ('title', 'extension', 'lft', 'rght', 'tree_id', 'level')
    list_filter = ('visible', )

    def extension(self, obj):
        if obj.app_extension:
            return Structure().apps.get(obj.app_extension).get('app_name')

    extension.allow_tags = True
    extension.short_description = u'Расширение'

    form = PageAdminForm


class ChunkAdmin(admin.ModelAdmin):
    """Текстовые блоки (чанки)"""
    admin_label = u'Управление контентом'

    list_display = ['__unicode__', 'is_html', 'content']
    list_editable = 'is_html',

    def get_form(self, request, obj=None, **kwargs):
        if hasattr(obj, 'id'):
            self.exclude = ['title']
        else:
            self.exclude = []

        return super(ChunkAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Page, PageAdmin)

admin.site.register(Fragment)


class SettingAdmin(admin.ModelAdmin):
    admin_label = u'Управление контентом'
    list_display = ('__unicode__', 'value', )
    list_editable = ('value', )
    list_resolve_foreign_keys = ['setting']

admin.site.register(Setting, SettingAdmin)