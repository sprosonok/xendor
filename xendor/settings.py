# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from django.conf import settings

from xendor.models import Setting

def settings_handler(sender, **kwargs):
    """Обработчик сигнала изменения настроек через админку"""

    if isinstance(kwargs.get('instance'), Setting):
        if not kwargs['created']:
            XendorSettings().regenerate()

post_save.connect(settings_handler)


DEFAULT_SETTING = {
    u'E-mail администратора': u'debug@yoursite.ru',
    u'Обратный e-mail': u'debug@yoursite.ru',
}

try:
    DEFAULT_SETTING.update(settings.XENDOR_SETTINGS)
except AttributeError:
    pass

class XendorSettings(object):
    """Представляет собой синглетон настроек сайта"""

    _instance = None

    parameters = {}

    module_settings = {}

    def __new__(cls, *dt, **mp):
        if cls._instance is None:
            cls._instance = object.__new__(cls,*dt,**mp)
            cls.parameters = {'meta': {}}
            cls.regenerate()

        return cls._instance

    @classmethod
    def add_settings(cls, key, value):
        cls.module_settings.update({key: value})

    def get(self, key):
        """Получение параметров"""

        return self.parameters['meta'].get(key) or self.parameters.get(key)


    def set_meta(self, title = None, description = None, breadcrumbs = None, activated_node = None, keywords = None):
        """Функция установки всех метатегов"""

        if title:
            self.parameters['meta']['meta_title'] = title

        if description:
            self.parameters['meta']['meta_description'] = description

        if keywords:
            self.parameters['meta']['meta_keywords'] = keywords

        if breadcrumbs:
            self.parameters['meta']['breadcrumbs_tail'] = breadcrumbs

        if activated_node:
            self.parameters['meta']['activated_node'] = activated_node

    @classmethod
    def regenerate(cls):
        """Обновление данных настроек из базы"""

        db_setting = dict([(i[1], i[2]) for i in Setting.objects.values_list()])

        for st in db_setting.keys():
            cls.parameters[st] = db_setting[st]

        cls.module_settings.update(DEFAULT_SETTING)

        for key, value in cls.module_settings.items():
            if not key in cls.parameters or not key in db_setting:
                item = Setting(name=key, value=value)
                item.save()
                cls.parameters[key] = value

    def clear_meta(self):
        """Очистка мета-параметров"""

        self.parameters['meta'] = {}
