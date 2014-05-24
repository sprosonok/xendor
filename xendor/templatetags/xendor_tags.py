# -*- coding: utf-8 -*-
"""Все универсальные темплейттеги и утилиты копировать сюда, нах"""

from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import stringfilter
from django.utils.html import mark_safe

from xendor.models import Page, Fragment
from xendor.settings import XendorSettings
from xendor.structure import Structure
from xendor.menu import Menu, _render_pars
from xendor.thumbnail import thumbnail, xendor_dummy
from xendor.templatetags.utils import _formater_1000, get_completed

import utils

register = template.Library()


@register.inclusion_tag('tags/fragment.html')
def fragment(fragment_name):
    """Вывод чанка (куска текста из модуля текстовые блоки)"""

    try:
        fragment = Fragment.objects.get(name=fragment_name)
    except Fragment.DoesNotExist:
        fragment = ''
        
    return {'fragmaent': fragment}

login_required
@register.assignment_tag
def subpages(page, smart_menu = False):
    """Создает в контексте шаблона переменную, использование: {% subpages for page as subpage_list %}

        а еще какой-то долбоеб че-то там добавил при этом потер нахуй все коменты и не написал че оно делает,
        ебать этого гандона грязной шваброй!
    """
    
    if type(page) == int:
        page = Page.objects.get(pk=int(page))
        
    pages = page.get_children().filter(visible=True)
    
    if bool(smart_menu) and page.level > 1 and pages.count() == 0:
        pages = page.parent.get_children().filter(visible=True)
    
    return pages


@register.inclusion_tag('dummy.html', takes_context=True)
def menu(context, params="", template='menu/menu.html'):
    """Рендер меню"""

    #проверка наличия контекста
    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}
    
    #инстанцирование класса меню
    try:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        menu = Menu(current_url, parameters=_render_pars(params))
    except Menu.MenuException:
        if settings.DEBUG:
            raise

        menu = None
        template = 'empty.html'

    context.update({'template': template, 'menu': menu, })
    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def level_menu(context, nodes=[], template='menu/level.html'):
    """Рендер уровня меню, вспомогательный тег, с помощью него реализуется многообразие отображений уровней"""

    context.update({'template': template, 'nodes': nodes})
    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def breadcrumbs(context, start_level=0, template='menu/breadcrumbs.html'):
    """Рендер крошки, start_level - уровень, с которого следует начинать"""
    
    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]

    path = list(Structure().tree.get_path_from_url(current_url, start_level))

    if XendorSettings().get('breadcrumbs_tail'):
        if isinstance(XendorSettings().get('breadcrumbs_tail'), (list, tuple)):
            path += XendorSettings().get('breadcrumbs_tail')
        elif isinstance(XendorSettings().get('breadcrumbs_tail'), dict):
            path.append(XendorSettings().get('breadcrumbs_tail'))

    context.update({
        'template': template,
        'path': path
    })

    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def metatitle(context, template='menu/metatitle.html'):
    """вывод метатега title
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры (meta_title or title)
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    title = XendorSettings().get('meta_title')

    if not title:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            title = current_node.meta_title or current_node.title
        else:
            title = Structure().tree.meta_title or Structure().tree.title
    if not title:
        try:
            main = Page.objects.get(is_main=True)
            title = main.meta_title or main.title
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'title': title
    })

    return context


@register.inclusion_tag('dummy.html', takes_context=True)
def metadescription(context, template='menu/metadescription.html'):
    """Вывод метатега description
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    description = XendorSettings().get('meta_description')

    if not description:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            description = current_node.meta_description or current_node.title
        else:
            description = Structure().tree.meta_description
    if not description:
        try:
            main = Page.objects.get(is_main=True)
            description = main.meta_description
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'description': description
    })

    return context

@register.inclusion_tag('dummy.html', takes_context=True)
def keywords(context, template='menu/metakeywords.html'):
    """Вывод метатега keywords
        Логика проста: выбираем метатег из
        - промежуточного хранилища в сеттингах
        - текущего элемента структуры
        - из главной страницы (которая должна хранить метатеги по-умолчанию)
    """

    try:
        request = context['request']
    except KeyError:
        return {'template': 'empty.html'}

    keywords = XendorSettings().get('meta_keywords')

    if not keywords:
        current_url = XendorSettings().get('activated_node') or request.get_full_path().split('?')[0]
        current_node = Structure().tree.get_element_by_url(current_url)
        if current_node:
            keywords = current_node.meta_keywords
        else:
            keywords = Structure().tree.meta_keywords
    if not keywords:
        try:
            main = Page.objects.get(is_main=True)
            keywords = main.meta_keywords
        except Page.DoesNotExist:
            return {'template': 'empty.html'}

    context.update({
        'template': template,
        'keywords': keywords
    })

    return context


@register.filter
@stringfilter
def xthumbnail(value, arg):
    """Делает тумбочку вписываемую в параметры
       использование {{ item.image|xthumbnail:'width;height;[fix;blank;wtm]' }}
       width – ширина
       height – высота 
       fix – обрезает картинку до нужного размера
       blank – заполняет белым или прозрачным вписывая в заданный размер
       wtm – добавляет ватермарк
    """
    
    return thumbnail(value, arg)

@register.filter
@stringfilter
def xdummy(value, arg):
    """Делает заглушку вместо картинки
       использование {{ line_size|xthumbnail:'width;height[color;background]' }}
       line_size - ширина линии
       width – ширина
       height – высота 
       color - цвет линии
       background - цвет бекграунда
       
       Пример: {{1|xdummy:'100;100;#2976bb;#f6f6f6'}}
    """
    
    return xendor_dummy(value, arg)

@register.inclusion_tag('tags/insert-get-parameter.html', takes_context=True)
def insert_get_parameter(context, value, name_get_parameter='page', exclude_vars=''):
    """мегаполезная шняга: формирует ссцыль для постранички, не трогает остальные get-параметры если они есть"""

    exclude_vars = exclude_vars.split(',')
    context.update({
        'page_string': '?' + '&'.join(reduce(lambda q, h: h[0] not in exclude_vars and q.append(unicode(h[0]) + '=' + unicode(h[1])) or q,
                (lambda d, p:
                    d.update({name_get_parameter: p}) or d
                )(dict(context['request'].GET.items()), value).items(), []))
    })
    return context

@register.simple_tag
def admin_image_upload_js():
    return utils.uploader_js


@register.inclusion_tag('tags/setting.html')
def get_setting(name):
    """Получает переменную из настроек сайта и выводит аз ис в шаблон"""

    value = XendorSettings().get(name)

    if value:
        return {'value': value}

    return {'value': ''}


@register.assignment_tag
def xendor_page(id):
    """ Возвращает страницу по ID или слагу """
    try:
        return Page.objects.get(pk=int(id))
    except Page.DoesNotExist:
        try:
            # костыль на случай если передали слаг вместо id (не документированная функция)
            return Page.objects.get(slug=id)
        except Page.DoesNotExist:
            return None


@register.filter
@stringfilter
def x1000(value):
    """Форматирует число добавляя пробелы для лучшей читабельности"""

    return mark_safe(utils._formater_1000(value))

@register.simple_tag
def xicon(icon):
    """ Render an icon """
    
    return '<span class="glyphicon glyphicon-{icon}"></span>'.format(icon=icon)


@register.assignment_tag
def xcontent_status():
    """ возвращает то насколько сайт наполнен (требует конфигурирования) """
    
    return get_completed()


##############################################
# Функции к удалению с версии 9.0
##############################################

@register.filter
@stringfilter
def x1000_filter(value):
    """
    DEPRICATED!
    Форматирует число добавляя пробелы для лучшей читабельности"""
    
    if settings.DEBUG:
        raise NotImplementedError(u'x1000_filter больше не поддерживается (с версии Xendor 8.1). Используйте "x1000"')
    return x1000(value)

@register.filter
@stringfilter
def get_page_link_by_id(id):
    if settings.DEBUG:
        raise NotImplementedError(u'get_page_link_by_id больше не поддерживается (с версии Xendor 8.1). Используйте "{% xendor_page id as object %}"')
    
    try:
        return Page.objects.get(pk=id).get_absolute_url()
    except Page.DoesNotExist:
        return '#'

@register.filter
@stringfilter
def get_page_by_id(id):
    if settings.DEBUG:
        raise NotImplementedError(u'get_page_by_id больше не поддерживается (с версии Xendor 8.1). Используйте "{% xendor_page id as object %}"')
    
    try:
        return Page.objects.get(pk=id)
    except Page.DoesNotExist:
        return '#'


@register.inclusion_tag('tags/page_content.html')
def get_page_content_by_id(id):
    if settings.DEBUG:
        raise NotImplementedError(u'get_page_content_by_id больше не поддерживается (с версии Xendor 8.1). Используйте "{% xendor_page id as object %}"')
    
    try:
        return {'page' : Page.objects.get(pk=int(id))}
    except Page.DoesNotExist:
        return {}
