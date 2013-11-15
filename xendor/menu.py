# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from xendor.models import Page
from xendor.structure import Structure

"""Этот кусок кода сучществует аж с начала 2010 года и много раз дописывался и модифицировался,
посему здесь возможно много бреда и непонятного неоптимального кода, но оно сцуко работает и проходит все тесты,
так что пока пусть существует в том виде в котором есть))) """


class Menu(object):
    """Класс меню, для каждой менюшки строится свой класс хранящий все ее параметры"""

    class MenuException(Exception):
        pass

    parent_node = 'ROOT'
    deep = 1
    level = None
    show_children = False
    show_hidden = False
    url = '/'
    nodes = []

    def __init__(self, url, *args, **kwargs):
        #обработка параметров
        self.url = url
        self.parent_node = kwargs.get('parent', self.parent_node)
        self.deep = kwargs.get('deep', self.deep)
        self.show_children = kwargs.get('show_children', self.show_children)
        self.show_hidden = kwargs.get('show_hidden', self.show_hidden)
        self.level = kwargs.get('level', self.level)

        #если параметры задаются через словарь parameters, то он имеет приоритет
        if kwargs.get('parameters', False):
            self.parent_node = kwargs['parameters'].get('parent', self.parent_node)

            #какой-то ебаный костыль - пересмотреть эту архитектуру в будущем
            if isinstance(self.parent_node, list) and len(self.parent_node) == 1:
                self.parent_node = self.parent_node[0]

            self.deep = kwargs['parameters'].get('deep', self.deep)
            self.show_children = kwargs['parameters'].get('show_children', self.show_children)
            self.show_hidden = kwargs['parameters'].get('show_hidden', self.show_hidden)
            self.level = kwargs['parameters'].get('level', self.level)
            self.parameters = kwargs.get('parameters', {})

        #инициация пунктов
        if self.parent_node == 'MAIN':
            try:
                main = Page.objects.get(is_main=True)
                if main.app_extension:
                    self.nodes = self._init_nodes(Structure().tree.get_element_by_url(Structure().get_app_url(main.app_extension)))
                else:
                    self.nodes = self._init_nodes(Structure().tree.get_element_by_url(main.get_absolute_url()))
            except Page.DoesNotExist:
                self.parent_node = 'ROOT'

        elif self.parent_node == u'CURRENT':
            self.nodes = self._init_nodes(Structure().tree.get_element_by_url(url))
        elif self.parent_node == u'PARENT':
            self.nodes = self._init_nodes(Structure().tree.get_parent_by_url(url))
        elif self.parent_node == 'ROOT':
            self.nodes = self._init_nodes(Structure().tree)
        else:

            parent_url = None

            if isinstance(self.parent_node[1], dict):
                parent_url = reverse(self.parent_node[0], kwargs=self.parent_node[1])

            if isinstance(self.parent_node[1], list) or isinstance(self.parent_node[1], tuple):
                if self.parent_node[1]:
                    parent_url = reverse(self.parent_node[0], args=self.parent_node[1])
                else:
                    parent_url = reverse(self.parent_node[0])

            if isinstance(self.parent_node, (str, unicode)):
                parent_url = reverse(self.parent_node)

            parent_structure_node = Structure().tree.get_element_by_url(parent_url)

            if parent_structure_node:
                self.nodes = self._init_nodes(parent_structure_node)
            else:
                raise self.MenuException('Ошибка меню! В структуре сайта отсутствует элемент указанный как корневой.')

    def _check_condition_by_parameters(self, node):
        """Проверка на соотвествие заданным параметрам"""

        accept = True  # результат прохождения теста по параметрам
        for k, v in node.parameters.items():
            if accept and self.parameters.get(k, False):
                if isinstance(self.parameters.get(k), (list, )):
                    accept = bool(sum(map(lambda i: i in v, self.parameters.get(k))))
                else:
                    accept = (unicode(self.parameters.get(k)) == unicode(v))

        return not accept
    
    def _init_nodes(self, source_node, level=0):
        """Построение дерева меню"""

        nodes = []

        for node in source_node.children:
            
            #обработка логики исключений и включений по параметрам
            if self._check_condition_by_parameters(node):
                continue

            if node.in_menu or self.show_hidden:
                added_node = {
                    'title': node.title,
                    'url': node.get_url(),
                    'children': [],
                    'active': False,
                    'current': False,
                    'level': level,
                    'parameters': node.parameters,
                }

                children = self._init_nodes(node, level + 1)

                if self.show_children:
                    added_node['children'] = children

                if list(node.get_path_from_url(self.url)):
                    added_node['active'] = True

                if self.url == node.get_url():
                    added_node['active'] = added_node['current'] = True

                if added_node['active']:
                    added_node['children'] = self._init_nodes(node, level+1)

                nodes.append(added_node)

        #чистим лишние уровни
        if level == 0:
            nodes = self._clear_nodes(nodes)
            if not self.level is None:
                nodes = self._select_level(nodes)

        return nodes

    def _clear_nodes(self, nodes):
        """ Очистка уровня меню до нужной глубины (глубина задается двумя параметрамим deep и level)"""

        cur_nodes = []
        for node_index in range(len(nodes)):
            if int(nodes[node_index]['level']) < int(self.deep):
                cur_nodes.append(nodes[node_index])
                cur_nodes[node_index]['children'] = self._clear_nodes(nodes[node_index]['children'])

        return cur_nodes

    def _select_level(self, nodes):
        """ Очистка уровня меню до нужной глубины (глубина задается двумя параметрамим deep и level)"""

        cur_nodes = []
        for node in nodes:
            if int(node['level']) == int(self.level):
                cur_nodes.append(node)
            else:
                cur_nodes += self._select_level(node['children'])

        return cur_nodes


def _render_url(raw_url):
    """
        Функция для разбора выражения для задания урла элемента меню
        выражение для элемента меню имеет вид:
        <название паттерна>&<список параметров>
        список параметров - либо перечисление через запятую var1,var2,var3,...
        либо (если используются именованные параметры) - varname1:var1, varname2:var2,...
        нельзя использовать одновременно оба варианта,
        это связанно с особенностями реализации функции reverse в джанге
    """

    urls = [list(x.split('&')) for x in raw_url.split('|')]
    for i in range(len(urls)):
        try:
            urls[i][1] = urls[i][1].split(',')
            for j in range(len(urls[i][1])):

                if ':' in urls[i][1][j]:
                    urls[i][1][j] = dict([urls[i][1][j].split(':')])

            tmp_dict = {}
            for j in range(len(urls[i][1])):
                if isinstance(urls[i][1][j], dict):
                    tmp_dict.update(urls[i][1][j])

            if len(tmp_dict):
                urls[i][1] = tmp_dict
        except:
            pass

    return urls


def _render_pars(params):

    #разбор параметров
    pars = {} #словарь с параметрами

    for item in params.split(';'):
        item = item.strip()# обрезаем пробелы по концам

        raw = item.split('=')
        if raw[0] != '':
            try:
                pars[raw[0]] = raw[1]
            except IndexError:
                pars[raw[0]] = True

    if pars.get('parent'):
        pars['parent'] = _render_url(pars['parent'])[0]

    return pars