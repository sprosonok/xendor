# -*- coding: utf-8 -*-
import json
from django.utils import translation
from django.conf import settings
from django.db.models.signals import post_delete, post_save

from xendor.models import Page

try:
    NEED_REGENERATE_MODELS = settings.NEED_REGENERATE_MODELS
except AttributeError:
    NEED_REGENERATE_MODELS = ('Page',)


class LanguageValue(object):
    def __init__(self, obj, attr):
        self.name = attr
        self.values = {}
        for lang in settings.LANGUAGES:
            if hasattr(obj, attr + '_' + lang[0]):
                self.values[lang[0]] = getattr(obj, attr + '_' + lang[0])

        self.default = getattr(obj, attr)

    def __unicode__(self):
        cur_language = translation.get_language()
        return self.values.get(cur_language, None) or self.default

    def __str__(self):
        return self.__unicode__()

    def __nonzero__(self):
        return bool(self.__unicode__())


class StructureNode:
    """Класс элемента структуры сайта"""

    class StructureNodeException(Exception):
        pass

    class SafeForStructureNodeException(Exception):
        pass

    def __init__(self,
                 title='ROOT',               #Выводимое название элемента структуры
                 url=None,                   #Урл элемента структуры
                 in_menu=True,               #Элемент выводится в меню
                 children=[],                #вложенные ноды
                 meta_title=None,            #метатег title
                 meta_description=None,      #метатег description
                 meta_keywords=None,         #метатег keywords
                 parameters={}               #доп, параметры нода
        ):
        self.title = title
        self.url = url
        self.meta_title = meta_title or ''
        self.meta_description = meta_description or ''
        self.meta_keywords = meta_keywords or ''
        self.in_menu = in_menu
        self.parameters = self._render_parameters(parameters)
        self.children = [
            StructureNode(
                title=item['title'],
                url=item['url'],
                in_menu=item.get('in_menu', True),
                children=item.get('children', []),
                meta_title=item.get('meta_title', None),
                meta_description=item.get('meta_description', None),
                meta_keywords=item.get('meta_keywords', None),
                parameters=item.get('parameters', {})
            )
            for item in children
        ]

    def _render_parameters(self, parameters):
        """подготовка параметров сайта. Принимает или словарь, или строку"""

        #@todo: добавить разбор параметров из строки представлющей собой валидный json
        if parameters:
            if isinstance(parameters, dict):
                return parameters
            elif isinstance(parameters, (str, unicode)):
                return {'page': parameters}

        return {}

    def get_element_by_url(self, url):
        """Ищет элемент структуры с заданным url"""

        url = url.split('?')[0]
        if self.get_url() == url:
            return self

        for item in self.children:
            tmp = item.get_element_by_url(url)
            if tmp:
                return tmp

        return None

    def get_parent_by_url(self, url):
        """Получение родительского нода по урлу"""

        url = url.split('?')[0]
        if self.get_url() == url:
            return self

        for item in self.children:
            tmp = item.get_element_by_url(url)
            if tmp:
                return item

        return None


    def _get_path_by_url(self, url):
        """рекурсивно строит путь от нода с определенным урлом до корня"""

        path = []
        if self.get_url() == url:
            path.append(self)
            return path

        for child in self.children:
            path = child._get_path_by_url(url)
            if path:
                path.append(child)
                return path

        return path


    def get_path_from_url(self, url, start_level=0, check_in_menu=True):
        """строит путь с определенного уровня до нода по урлу"""

        if check_in_menu:
            if start_level:
                return reversed([n for n in self._get_path_by_url(url) if n.in_menu][1:-start_level])
            else:
                return reversed([n for n in self._get_path_by_url(url) if n.in_menu][1:])
        else:
            if start_level:
                return reversed(self._get_path_by_url(url)[1:-start_level])
            else:
                return reversed(self._get_path_by_url(url)[1:])

    def get_url(self):
        """Небольшой хелпер для обработки callable объектов генерирующих урл"""

        if callable(self.url):
            try:
                return self.url()
            except:
                pass

        return self.url

    def __unicode__(self):
        return self.title

    def as_json(self):
        """возвращает нод в виде json-a"""

        return {
            'title': self.title,
            'url': self.get_url(),
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'meta_keywords': self.meta_keywords,
            'in_menu': self.in_menu,
            'parameters': self.parameters,
            'children': [child.as_json() for child in self.children]
        }


class Structure(object):
    """Представляет собой синглетон структуры сайта"""

    _instance = None

    apps = {}

    def __new__(cls, *dt, **mp):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *dt, **mp)

            for app in settings.INSTALLED_APPS:
                __import__(app, {}, {}, ['app_extend'])

            cls._instance._generate()

        return cls._instance

    def _generate(self, regenerate=False):
        """Генерирует базовую структуру сайта (внутренний метод)"""

        self.tree = StructureNode()

        if regenerate:
            for app in settings.INSTALLED_APPS:
                try:
                    reload(__import__(app + '.app_extend', {}, {}, ['app_extend']))
                except:
                    pass

        for root_node in Page.objects.root_nodes().filter(visible=True):
            self.tree.children.append(self._sub_tree(root_node))

    def _sub_tree(self, page):
        """Генерирует подменю для текущего узла дерева"""

        if page.is_main:
            self.tree.title = LanguageValue(page, 'menu_title') or LanguageValue(page, 'title')
            self.tree.meta_title = LanguageValue(page, 'meta_title') or LanguageValue(page, 'title')
            self.tree.meta_description = LanguageValue(page, 'meta_description') or LanguageValue(page, 'title')
            self.tree.meta_keywords = page.meta_keywords

        node = StructureNode(
            title=LanguageValue(page, 'menu_title') or LanguageValue(page, 'title'),
            url=page.menu_url or page.get_absolute_url,
            in_menu=page.in_menu,
            children=[],
            meta_title=LanguageValue(page, 'meta_title') or LanguageValue(page, 'title'),
            meta_description=LanguageValue(page, 'meta_description') or LanguageValue(page, 'title'),
            meta_keywords=page.meta_keywords,
            parameters=page.parameters
        )

        try:
            app = self.apps[page.app_extension]
            node.url = app['node_url']
            node.meta_title = app.get('meta_title', node.meta_title)
            node.meta_description = app.get('meta_description', node.meta_description)
            node.meta_keywords = app.get('meta_keywords', node.meta_keywords)
            node.parameters.update(app.get('parameters', {}))

            if app['safe_for_structure']:
                raise StructureNode.SafeForStructureNodeException()

            node.children = [
                StructureNode(
                    title=item['title'],
                    url=item['url'],
                    in_menu=item.get('in_menu', True),
                    children=item.get('children', []),
                    meta_title=item.get('meta_title', ''),
                    meta_description=item.get('meta_description', ''),
                    meta_keywords=item.get('meta_keywords', ''),
                    parameters=item.get('parameters', {}),
                )
                for item in self.apps[page.app_extension]['children']
            ]

        except (KeyError, StructureNode.SafeForStructureNodeException):
            for subnode in page.get_children().filter(visible=True):
                node.children.append(self._sub_tree(subnode))

        return node

    def register_app (self, app_id, app_name, node_url, children=[], node_parameters={},  safe_for_structure=False):
        """Регистрация приложения"""

        self.apps[app_id] = {
            'app_name': app_name,
            'node_url': node_url,
            'children': children,
            'parameters': node_parameters,
            'safe_for_structure': safe_for_structure
        }

    def get_app(self, app_id):
        """Получить данные аппликейшна по его id"""

        try:
            return self.apps[app_id]
        except KeyError:
            return None

    def get_app_url(self, app_id):
        """Получение урла аппликейшна"""

        app = self.get_app(app_id)
        if app:
            if callable(app['node_url']):
                try:
                    return app['node_url']()
                except:
                    pass
            else:
                return app['node_url']

        return None

    def regenerate(self, *args, **kwargs):
        instance = kwargs.get('instance').__class__.__name__

        generate_items = NEED_REGENERATE_MODELS
        if instance in generate_items:
            self._generate(True)

    def get_structure_as_json(self):
        """Отладочная хрень, возвращает структуру сайта в виде json-a"""

        return self.tree.as_json()

    def get_structure_as_jsons(self):
        """Отладочная хрень, возвращает структуру сайта в виде json-a отформатированного для вывода на экран"""

        return json.dumps(self.tree.as_json(), indent=4)


#регенерация структуры при изменении структурообразующих элементов моделей
post_delete.connect(Structure().regenerate)
post_save.connect(Structure().regenerate)
