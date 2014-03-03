# -*- coding: utf-8 -*-
import datetime
import hashlib

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.loader import render_to_string

conversion = {
    u'а' : 'a',
    u'б' : 'b',
    u'в' : 'v',
    u'г' : 'g',
    u'д' : 'd',
    u'е' : 'e',
    u'ё' : 'e',
    u'ж' : 'zh',
    u'з' : 'z',
    u'и' : 'i',
    u'й' : 'j',
    u'к' : 'k',
    u'л' : 'l',
    u'м' : 'm',
    u'н' : 'n',
    u'о' : 'o',
    u'п' : 'p',
    u'р' : 'r',
    u'с' : 's',
    u'т' : 't',
    u'у' : 'u',
    u'ф' : 'f',
    u'х' : 'h',
    u'ц' : 'c',
    u'ч' : 'ch',
    u'ш' : 'sh',
    u'щ' : 'sch',
    u'ь' : "",
    u'ы' : 'y',
    u'ь' : "",
    u'э' : 'e',
    u'ю' : 'ju',
    u'я' : 'ja',
    u'А' : 'A',
    u'Б' : 'B',
    u'В' : 'V',
    u'Г' : 'G',
    u'Д' : 'D',
    u'Е' : 'E',
    u'Ё' : 'E',
    u'Ж' : 'ZH',
    u'З' : 'Z',
    u'И' : 'I',
    u'Й' : 'J',
    u'К' : 'K',
    u'Л' : 'L',
    u'М' : 'M',
    u'Н' : 'N',
    u'О' : 'O',
    u'П' : 'P',
    u'Р' : 'R',
    u'С' : 'S',
    u'Т' : 'T',
    u'У' : 'U',
    u'Ф' : 'F',
    u'Х' : 'H',
    u'Ц' : 'C',
    u'Ч' : 'CH',
    u'Ш' : 'SH',
    u'Щ' : 'SCH',
    u'Ъ' : "",
    u'Ы' : 'Y',
    u'Ь' : "",
    u'Э' : 'E',
    u'Ю' : 'JU',
    u'Я' : 'JA',
    u' ' : '-',
    u'/' : '/',
    }


def cyr2lat(s):
    """Преобразование последовательности символов на русском в транслит"""

    retval = ""
    for c in s:
        try:
            c = conversion[c]
            retval += c
        except KeyError:

            if ('A' <= c <= 'Z') or ('a' <= c <= 'z')  or ('0' <= c <= '9'):
                retval += c
            else:
                retval += '-'

    retval = retval[:254]
    return retval


def translit(path, file):
    """Возвращает имя файла транслитом"""

    basename, format = unicode(file).rsplit('.', 1)
    try:
        basename, name = basename.rsplit('/', 1)
    except:
        name = basename

    name = cyr2lat(name)

    return u"%s/%s" % (path, name + '.' + format)


def _is_unique(instance, slug):
    """Проверка уникальности слага для заданной модели"""

    if not slug: return False

    try:
        if instance.pk:
            instance.__class__.objects.exclude(pk=instance.pk).get(slug=slug)
        else:
            instance.__class__.objects.get(slug=slug)
        return False
    except instance.__class__.DoesNotExist:
        return True

def _clean_dash(source, exclude_slash):
    """Убираем повторяющиеся тире и опционально / из строки"""

    while u'--' in source:
        source = source.replace(u'--', u'-')

    return u''.join([char.replace('/','_') for char in source.strip('-')]) 

def generate_slug(instance, source, exclude_slash = True, need_unique = True):
    """Генерация уникального слага для заданной модели"""

    num, generator = 0, lambda s: _clean_dash(cyr2lat(s.strip()).lower().replace(' ', '-'), exclude_slash)
    
    if need_unique:
        while not _is_unique(instance, generator(source + (u'-' + unicode(num)) * int(bool(num)))): num += 1
    
    return generator(source + (u'-' + unicode(num)) * int(bool(num)))

def getmd5(path, file='_.jpg'):
    basename, format = file.rsplit('.', 1)

    return u"%s/%s" % (path, 'a_' + hashlib.md5(unicode(datetime.datetime.now())).hexdigest() + '.' + format)


def make_page(request, object_list, **kwargs):
    """Хелпер для быстрой генерации постранички
        Дефолтный рендер процессор и шаблон формирует ссылки безопасные для прочих get параметров
        Использование:
            - views.py:
                page = make_page(request, Item.objects.all(), count_per_page=2, page_get_parameter='item_page')
            - шаблон:
                <!-- список итемов -->
                - for item in page.object_list
                    = item

                <!-- ссылки на постраничку -->
                = page.render
        Список возможных параметров - смотреть в коде в словаре default
    """

    #значения по умолчанию
    default = {
        'count_per_page': request.session.get('item_per_page', 10), #количество записей на страницу
        'page_range': 3,  #диапазон страниц
        'page_get_parameter': 'page', #гет параметр отвечающий за значение текущей страницы
        'render_processor': None,    #рендер процессор (функция, которая рендерит шаблон постранички)
        'template': 'utils/_paginator.html', #шаблон постранички
    }

    #инициализация параметров
    default.update(kwargs)

    paginator = Paginator(object_list, default['count_per_page'])

    try:
        page = int(request.GET.get(default['page_get_parameter'], '1'))
    except ValueError:
        page = 1

    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    def render_processor(request, page, **kwargs):
        """Процессор рендеринга, на случай необходимости
            расширения функционала постранички пишется отдельная функция для рендеринга
            (а то заебали, блеадь, в каждом проекте своя ебнутая постраничка и куда ни ткнись ни хуя не работает)"""

        return render_to_string(
            kwargs['template'],
            {
                'request': request,
                'page': page,
                'page_range': (lambda d, s, e: d[s:e])(range(1, page.paginator.num_pages + 1),
                                      (lambda n: n >= 0 and n or 0)(page.number - 1 - kwargs['page_range']),
                                       page.number + kwargs['page_range']),
                'page_get_parameter': kwargs['page_get_parameter'],
                'count_per_page': request.session.get('item_per_page', 10)
            })

    def renderer():
        """Формируем замыкание на параметры конкретного пагинатора (необходимо для работы внешнего render_processor-а)"""
        return (callable(default['render_processor']) and default['render_processor'] or render_processor)(request, page, **default)

    #TODO: дописать возможность передачи рендерера по названию в виде 'app.package.module.calable_object'
    page.render = renderer
    return page


def make_page_for_cbv(request, object_list, **kwargs):
    """Хелпер для быстрой генерации постранички
        Дефолтный рендер процессор и шаблон формирует ссылки безопасные для прочих get параметров
        Использование:
            - views.py:
                page = make_page(request, Item.objects.all(), count_per_page=2, page_get_parameter='item_page')
            - шаблон:
                <!-- список итемов -->
                - for item in page.object_list
                    = item

                <!-- ссылки на постраничку -->
                = page.render
        Список возможных параметров - смотреть в коде в словаре default
    """

    #значения по умолчанию
    default = {
        'count_per_page': request.session.get('item_per_page', 10), #количество записей на страницу
        'page_range': 3,  #диапазон страниц
        'page_get_parameter': 'page', #гет параметр отвечающий за значение текущей страницы
        'render_processor': None,    #рендер процессор (функция, которая рендерит шаблон постранички)
        'template': 'utils/_paginator.html', #шаблон постранички
    }

    #инициализация параметров
    default.update(kwargs)

    paginator = Paginator(object_list, default['count_per_page'])

    try:
        page = int(request.GET.get(default['page_get_parameter'], '1'))
    except ValueError:
        page = 1

    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    def render_processor(request, page, **kwargs):
        """Процессор рендеринга, на случай необходимости
            расширения функционала постранички пишется отдельная функция для рендеринга
            (а то заебали, блеадь, в каждом проекте своя ебнутая постраничка и куда ни ткнись ни хуя не работает)"""

        return render_to_string(
            kwargs['template'],
            {
                'request': request,
                'page': page,
                'page_range': (lambda d, s, e: d[s:e])(range(1, page.paginator.num_pages + 1),
                    (lambda n: n >= 0 and n or 0)(page.number - 1 - kwargs['page_range']),
                    page.number + kwargs['page_range']),
                'page_get_parameter': kwargs['page_get_parameter'],
                'count_per_page': request.session.get('item_per_page', 10)
            })

    def renderer():
        """Формируем замыкание на параметры конкретного пагинатора (необходимо для работы внешнего render_processor-а)"""
        return (callable(default['render_processor']) and default['render_processor'] or render_processor)(request, page, **default)

    #TODO: дописать возможность передачи рендерера по названию в виде 'app.package.module.calable_object'
    paginator.render = renderer
    return paginator