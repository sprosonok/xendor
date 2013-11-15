# -*- coding: utf-8 -*-
from django.utils.functional import curry

from xendor.thumbnail import thumbnail


def _image_field(dbfield, size, model_admin, item):
    """делаем превьюшку"""
    
    image = getattr(item, dbfield)
    image_path = thumbnail(str(image), size).replace('\\','/')
    return '<a href="'+ str(item.pk) +'/"><img src="'+ str(image_path) +'"/></a>'


def image_field(db_field, column_name, size='60x60'):
    """Универсальный констуктор полей для изображения"""
    
    result = curry(_image_field, db_field, size)
    result.short_description = column_name
    result.allow_tags = True
    
    return result









