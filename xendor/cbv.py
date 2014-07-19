# -*- coding: utf-8 -*-
"""Небольшой набор компонентов для class based view """
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import get_current_site
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.query_utils import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import simplejson
from django.views.generic.base import View, TemplateResponse, RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib import messages

from xendor.models import Page
from xendor.utils import make_page_for_cbv
from xendor.settings import XendorSettings
from xendor.thumbnail import thumbnail


class ContentTypeMixin(View):
    """Миксин для обработки ссылки на контент тайп оъект
        подразумевается, что паттерн урла содержит переменные:
        - content_type_id - ид типа
        - object_id - ид объекта
        Например: url(r'^remove-like/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', RemoveLike.as_view(), name='likes-remove'),


        миксин вычисляет:
         - объект контент тайпа: self.object_type
         - сам объект: self.object

        в контексте шаблона соотвественно добавляются переменные object и object_type
    """

    object_type = None
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object_type = ContentType.objects.get(pk=kwargs['content_type_id'])
        self.object = self.object_type.get_object_for_this_type(pk=kwargs['object_id'])

        return super(ContentTypeMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContentTypeMixin, self).get_context_data(**kwargs)
        context.update({
            'object_type': self.object_type,
            'object': self.object
        })
        return context


class RefererRedirectWithMessage(RedirectView):
    """Миксин для обработки действий требующих редиректа обратно на страницу
        (лайки, добавление в корзину и т.п.)
        добавляет в мессадж фреймворк прописанное сообщение

        атрибуты:
            action_message = u'' - текст сообщения
            action - callable объект реализующий функционал
            post_action - callable объект реализующий отдельный функционал для post запросов

        если post_action не задан и пост-запросы возможны (по умолчанию - да),
            то выполняется тот же функционал что и для гет запросов
    """

    http_method_names = [u'get', u'post']
    permanent = False
    action_message = u''

    action = lambda o: None

    def get_redirect_url(self, *args, **kwargs):
        messages.add_message(self.request, messages.SUCCESS, self.action_message)
        return self.request.META.get('HTTP_REFERER') or '/'

    def get(self, request, *args, **kwargs):
        self.action()
        return super(RefererRedirectWithMessage, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if getattr(self, 'post_action', None):
            self.post_action()
        else:
            self.action()
        return super(RefererRedirectWithMessage, self).post(request, *args, **kwargs)


class MultiSortingMixin(ListView):
    """Миксин сортировки по полям
        хуй его знает как оно работает, но нужно задать поля для сортировки вот так:
        sort_field = (('price', 'по цене', True), ('name', 'по названию', True), )

        а в шаблоне нужно написать что-то вроде:
        {% load xendor_tags %}

        {% if sorting|length > 0 %}

        {% endif %}

        {% for field in sorting %}
            {% if field.3 %}
                {% if field.1 == 'asc' %}
                    &uarr;
                {% endif %}

                {% if field.1 == 'desc' %}
                    &darr;
                {% endif %}

            {% endif %}
                <a href="{% insert_get_parameter field.1 field.0 %}" class="{{ field.3 }} {% if field.3 %}{{ field.1 }}{% endif %}">{{ field.2 }}</a>
            {% if field.3 %}
                <a href="{% insert_get_parameter field.1 field.0 field.0 %}" class="del-link"><sup>X</sup></a>
            {% endif %}
            {% if not forloop.last %} | {% endif %}
        {% endfor %}

        сортировка получилась мульти, надо наверное дописать на обычную, но блин лень
    """

    sort_field = ()

    def get_queryset(self):
        pars = []
        for field in self.sort_field:
            if self.request.GET.get(field[0]):
                if field[2]:
                    pars = [unicode(self.request.GET.get(field[0]) == 'desc' and '-' or '') + field[0]]
                    break
                else:
                    pars.append(unicode(self.request.GET.get(field[0]) == 'desc' and '-' or '') + field[0])

        return super(SortingMixin, self).get_queryset().order_by(*pars)

    def get_context_data(self, **kwargs):

        context = super(SortingMixin, self).get_context_data(**kwargs)

        context.update({
            'sorting': [(f[0], self.request.GET.get(f[0]) == 'asc' and 'desc' or 'asc', f[1],
                         self.request.GET.get(f[0]) and 'active' or '') for f in self.sort_field]
        })

        return context


class SortingMixin(ListView):
    """Миксин сортировки по полям
        хуй его знает как оно работает, но нужно задать поля для сортировки вот так:
        sort_field = (('price', 'по цене', True), ('name', 'по названию', True), )

        а в шаблоне нужно написать что-то вроде:
        {% load xendor_tags %}

        {% if sorting|length > 0 %}
            <ul class="list-inline list-unstyled sorting">
                <li>Сортировка: </li>
                {% for field in sorting %}
                    <li class="{{ field.3 }} {% if field.3 %}{{ field.1 }}{% endif %}">
                        <a href="{% insert_get_parameter field.1 field.0 field.4 %}">
                            {{ field.2 }} <span>{% if field.3 %}
                                {% if field.1 == 'asc' %}
                                    &uarr;
                                {% endif %}

                                {% if field.1 == 'desc' %}
                                    &darr;
                                {% endif %}

                            {% endif %}
                        </span></a>
                    </li>
                {% endfor %}
            </ul>
        {% endif %}
    """

    sort_field = ()

    def get_queryset(self):
        pars = []
        for field in self.sort_field:
            if self.request.GET.get(field[0]):
                if field[2]:
                    pars = [unicode(self.request.GET.get(field[0]) == 'desc' and '-' or '') + field[0]]
                    break
                else:
                    pars.append(unicode(self.request.GET.get(field[0]) == 'desc' and '-' or '') + field[0])

        return super(SortingMixin, self).get_queryset().order_by(*pars)

    def get_context_data(self, **kwargs):

        context = super(SortingMixin, self).get_context_data(**kwargs)

        context.update({
            'sorting': [(
                            f[0],                                                          #название поля модели
                            self.request.GET.get(f[0]) == 'asc' and 'desc' or 'asc',       #порядок сортировки
                            f[1],                                                          #человекопонятное название
                            self.request.GET.get(f[0]) and 'active' or '',                 #статус фильтра
                            ','.join([i[0] for i in self.sort_field if i != f])            #поля для исключения
                        ) for f in self.sort_field]
        })

        return context


class PageAppExtensionMixin(object):
    """Используется для вьюшек ассоциированных через app_extension каким-либо модулем
        Добавляет объект страницы с ассоциированным модулем в контекст в виде переменной page
    """

    app_extension = None

    def get_context_data(self, **kwargs):
        context = super(PageAppExtensionMixin, self).get_context_data(**kwargs)

        try:
            page = Page.objects.get(app_extension=self.app_extension)
        except Page.DoesNotExist:
            page = None

        context.update({
            'page': page
        })
        return context


class ListByObjectSlugMixin(ListView):
    """Класс строящий список по внешнему ключу (ForeignKey) объекта передаваемого по слагу
        помещает в контекст объект слагификации в переменной object
        фильтрует список по этому объекту
        необходимые параметры:
        slugified_model = <класс модели указанный в ForeignKey>
        поле ключа должно быть именем класса модели на которую указывает ключ в ловеркейсе
    """

    slugified_model = None

    def get(self, request, *args, **kwargs):
        if self.slugified_model:
            self.slugified_object = get_object_or_404(self.slugified_model, slug=self.kwargs.get('slug'))
        else:
            self.slugified_object = None
        return super(ListByObjectSlugMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListByObjectSlugMixin, self).get_context_data(**kwargs)
        if self.slugified_object:
            context.update({
                'object': self.slugified_object
            })
        return context
    
    def get_object(self):
        return self.slugified_object
    
    def get_queryset(self):
        if self.slugified_object:
            call_dict = {self.slugified_model.__name__.lower(): self.slugified_object}
            return super(ListByObjectSlugMixin, self).get_queryset().filter(**call_dict)
        else:
            return super(ListByObjectSlugMixin, self).get_queryset()

class ListByObjectPkMixin(ListView):
    """Класс строящий список по внешнему ключу (ForeignKey) объекта передаваемого по ID
        помещает в контекст объект слагификации в переменной object
        фильтрует список по этому объекту
        необходимые параметры:
        slugified_model = <класс модели указанный в ForeignKey>
        поле ключа должно быть именем класса модели на которую указывает ключ в ловеркейсе
    """

    pk_model = None

    def get(self, request, *args, **kwargs):
        if self.pk_model:
            self.pk_object = get_object_or_404(self.pk_model, pk=self.kwargs.get('pk'))
        else:
            self.pk_object = None
        return super(ListByObjectPkMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ListByObjectPkMixin, self).get_context_data(**kwargs)
        if self.pk_object:
            context.update({
                'object': self.pk_object
            })
        return context
    
    def get_object(self):
        return self.pk_object
    
    def get_queryset(self):
        if self.pk_object:
            call_dict = {self.pk_model.__name__.lower(): self.pk_object}
            return super(ListByObjectPkMixin, self).get_queryset().filter(**call_dict)
        else:
            return super(ListByObjectPkMixin, self).get_queryset()

class ListByTreeObjectSlugMixin(ListByObjectSlugMixin):
    """
    Аналогично классу ListByObjectSlugMixin,
    только учитывает всех нескрытых потомков передданного по слагу объекта категории
    """

    def get_queryset(self):
        if self.slugified_object:
            call_dict = {
                self.slugified_model.__name__.lower() + '__in': [
                    i[0] for i in self.slugified_object.get_descendants(
                        include_self=True).filter(visible=True).values_list('pk')]}
            return super(ListByObjectSlugMixin, self).get_queryset().filter(**call_dict).distinct()
        else:
            return super(ListByObjectSlugMixin, self).get_queryset()


class SubtreeByObjectSlugMixin(ListView):
    """Миксин строящий список чайлдов нода по слагу нода
        в списке наследования ставить в конце!
    """

    slugified_object = None

    def get(self, request, *args, **kwargs):
        self.slugified_object = get_object_or_404(self.model, slug=self.kwargs.get('slug'))

        return super(SubtreeByObjectSlugMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubtreeByObjectSlugMixin, self).get_context_data(**kwargs)
        context.update({
            'object': self.slugified_object
        })
        return context

    def get_queryset(self):

        return self.slugified_object.get_children()


class PaginatedListMixin(ListView):
    """Класс с преднастроенным пагинатором
        вызов постранички в шаблоне: {{ paginator.render }}
    """
    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return make_page_for_cbv(self.request, queryset, count_per_page=per_page)


class VisibleObjectListMixin(ListView):
    """Класс добавляющий в кверисет условие visible=True"""

    def get_queryset(self):
        return super(VisibleObjectListMixin, self).get_queryset().filter(visible=True)


class ToStructureMixin(View):
    """Класс для интеграции вьюшки в структуру сайта, содержит ряд полей для описания места в структуре
    допустимо задавать поля как callable объекты (учитывать при этом,
    что приаттаченые таким образом лямбды считаются методами класса
    и получают на входе инстанс класса первым аргументом)
    """

    meta_title = ''
    meta_description = ''
    meta_keywords = ''
    
    breadcrumbs = []
    activated_node = None

    def _for_callable(self, field):
        return callable(field) and field() or field

    def get_meta_title(self):
        return self._for_callable(self.meta_title)

    def get_meta_description(self):
        return self._for_callable(self.meta_description)

    def get_meta_keywords(self):
        return self._for_callable(self.meta_keywords)

    def get_breadcrumbs(self):
        breadcrumbs = self._for_callable(self.breadcrumbs)
        if isinstance(breadcrumbs, (str, unicode)):
            return [{'title': breadcrumbs, 'url': '', 'in_menu': True},]
        return breadcrumbs

    def get_activated_node(self):
        return self._for_callable(self.activated_node)

    def dispatch(self, request, *args, **kwargs):
        result = super(ToStructureMixin, self).dispatch(request, *args, **kwargs)

        XendorSettings().set_meta(
            title=self.get_meta_title() or None,
            description=self.get_meta_description() or None,
            breadcrumbs= self.get_breadcrumbs() or None,
            activated_node=self.get_activated_node() or None,
            keywords=self.get_meta_keywords() or None,
        )
        return result


class WithMailer(object):
    """Класс добавляющий метод для мейлинга
    выполнен в виде класса для того чтобы иметь доступ к локальному контексту вьюшки"""

    def send_mail(self, title, template, context, mail_to, mail_from=None):
        mail_from = mail_from or XendorSettings().get(u'Обратный e-mail')
        default_context = {}
        current_site = get_current_site(self.request)

        default_context['site_name'] = current_site.name
        default_context['domain'] = current_site.domain
        default_context['protocol'] = 'http'
        default_context.update(context)

        mail_to = not isinstance(mail_to, (list, tuple)) and mail_to.split(',') or mail_to

        email_message = EmailMessage(title.format(**default_context), render_to_string(template, default_context), mail_from, mail_to)
        email_message.content_subtype = 'html'
        email_message.send()


class SearchByModelMixin(ListView):
    """Миксин для поиска по модели
        указываем атрибут search_fields в котором список полей по которым ищем.
        миксин подхватывает из реквеста гет парамер search_get_parameter и формирует условие для поиска.
        В остальном обычный ListVeiw
    """

    search_fields = []
    search_get_parameter = 's'

    def get_queryset(self):
        if self.request.GET.get(self.search_get_parameter):
            return super(SearchByModelMixin, self).get_queryset().filter(reduce(lambda f, s: f | s,
                [Q(**{(f + '__icontains'): self.request.GET.get(self.search_get_parameter)}) for f in self.search_fields]))
        else:
            return super(SearchByModelMixin, self).get_queryset().none()

    def get_context_data(self, **kwargs):
        context = super(SearchByModelMixin, self).get_context_data(**kwargs)
        context[self.search_get_parameter] = self.request.GET.get(self.search_get_parameter)
        return context


class ScaffoldMeta(type):

    def __new__(cls, *args, **kwargs):
        views = []
        attrs = {}
        map(lambda s: attrs.update([(n, getattr(s, n)) for n in dir(s) ]), args[1])
        attrs.update(args[2])
        for attr, value in attrs.items():
            try:
                if issubclass(value, View):
                    setattr(value, 'model', attrs['model'])
                    views.append(attr)
            except:
                pass

        for attr, value in attrs.items():
            for n in views:
                if n.lower() in attr:
                    setattr(attrs[n], attr.replace(n.lower() + '_', ''), value)

        obj = type(args[0], args[1], args[2])

        for attr, value in attrs.items():
            try:
                if issubclass(value, View):
                    setattr(value, 'scaffold', obj)
            except:
                pass

        return obj


class CRUDScaffold(object):

    slugify = False
    url_namespace = None

    list_paginate_by = 10

    @classmethod
    def get_url_namespace(cls):
        return cls.url_namespace

    @classmethod
    def get_url_patterns(cls):
        from django.conf.urls import url, patterns
        if cls.slugify:
            scaffold_patterns = patterns('',
                url(r'^$', cls.List.as_view(), name = cls.get_url_namespace() + '-list'),
                url(r'^create/$', cls.Create.as_view(), name = cls.get_url_namespace() + '-create'),
                url(r'^(?P<slug>\w+)/$', cls.Detail.as_view(), name = cls.get_url_namespace() + '-item'),
                url(r'^(?P<slug>\w+)/delete/$', cls.Delete.as_view(), name = cls.get_url_namespace() + '-delete'),
                url(r'^(?P<slug>\w+)/edit/$', cls.Update.as_view(), name = cls.get_url_namespace() + '-update'),
            )
        else:
            scaffold_patterns = patterns('',
                url(r'^$', cls.List.as_view(), name = cls.get_url_namespace() + '-list'),
                url(r'^create/$', cls.Create.as_view(), name = cls.get_url_namespace() + '-create'),
                url(r'^(?P<pk>\w+)/$', cls.Detail.as_view(), name = cls.get_url_namespace() + '-item'),
                url(r'^(?P<pk>\w+)/delete/$', cls.Delete.as_view(), name = cls.get_url_namespace() + '-delete'),
                url(r'^(?P<pk>\w+)/edit/$', cls.Update.as_view(), name = cls.get_url_namespace() + '-update'),
            )
        return scaffold_patterns

    class List(PaginatedListMixin, ListView):
        pass

    class Detail(ToStructureMixin, DetailView):
        meta_title = meta_description = breadcrumbs = lambda o: o.get_object().title

        def get_activated_node(self):
            return reverse(self.scaffold.get_url_namespace() + '-list')

    class Create(CreateView):
        pass

    class Update(UpdateView):
        pass

    class Delete(DeleteView):
        def get_success_url(self):
            return reverse(self.scaffold.get_url_namespace() + '-list')


class JSONResponse(HttpResponse):
    """JSON response class."""

    def __init__(self, data_obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = simplejson.dumps(data_obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


class JSONResponseMixin(object):
    """Миксин для форматирования респонза в джейсон,
        автоматом оборачивает нужными хедерами и посылает в браузер контекст вьюшки
        Использовать совместно с TemplateView"""

    response_class = JSONResponse
    status_code = None

    def _response_mimetype(self):
        if "application/json" in self.request.META['HTTP_ACCEPT']:
            return "application/json"
        else:
            return "text/plain"

    def get_statuscode(self):
        return self.status_code

    def render_to_response(self, context, **response_kwargs):
        """Return response with json-formatted context object"""

        return self.response_class(
            data_obj=context,
            mimetype=self._response_mimetype(),
            status=self.get_statuscode(),
            **response_kwargs)


class JSONPResponse(HttpResponse):
    """JSONP response class."""

    def __init__(self, callback, data_obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = callback + '(' + simplejson.dumps(data_obj, **json_opts) + ');'
        super(JSONPResponse, self).__init__(content, mimetype, *args, **kwargs)


class JSONPResponseMixin(object):
    """Миксин для форматирования респонза в джейсон,
        автоматом оборачивает нужными хедерами и посылает в браузер контекст вьюшки
        Использовать совместно с TemplateView"""

    response_class = JSONPResponse

    def render_to_response(self, context, **response_kwargs):
        """Return response with json-formatted context object"""

        return self.response_class(
            callback=self.request.GET.get('callback'),
            data_obj=context,
            mimetype='text/javascript;',
            status=200,
            **response_kwargs)


class ImageAdminMeta(type):

    def __new__(cls, *args, **kwargs):

        attrs = {}
        map(lambda s: attrs.update([(n, getattr(s, n)) for n in dir(s) ]), args[1])
        attrs.update(args[2])

        obj = type(args[0], args[1], attrs)

        setattr(attrs['ImagesCreateView'], 'model', attrs['image_model'])
        setattr(attrs['ImagesCreateView'], 'item_class', attrs['model'])
        setattr(attrs['ImagesCreateView'], 'delete_url_prefix', attrs['delete_url_prefix'])
        setattr(attrs['ImagesDeleteView'], 'model', attrs['image_model'])

        return obj


class ImageAdmin(object):
    """класс для добавления в админку клевого интерфейса под загрузку фотков
        использовать:

        __metaclass__ = ImageAdminMeta

        model = Item
        image_model = ItemImage #в модели картинки название поля - ключа на модель владельца должно быть названием модели в ловеркейсе

        delete_url_prefix = 'catalog_item_change'
    """

    class ImagesCreateView(CreateView):

        template_name = 'admin/image-upload.html'

        def get_form_class(self):
            from django.forms.models import modelform_factory
            return modelform_factory(self.model, exclude=(self.item_class.__name__.lower(),))

        def get(self, request, *args, **kwargs):
            self.item = get_object_or_404(self.item_class, pk=int(args[0]))
            self.object = None
            form_class = self.get_form_class()
            form = self.get_form(form_class)

            return TemplateResponse(
                request=self.request,
                template=self.get_template_names(),
                context=self.get_context_data(form=form)
            )

        def get_context_data(self, **kwargs):

            context = super(CreateView, self).get_context_data(**kwargs)
            context['back_link'] = reverse('admin:' + self.delete_url_prefix, args=[self.item.pk])
            context['material'] = self.item
            context['images'] = self.item.get_admin_image().order_by('pk')
            return context

        def post(self, request, *args, **kwargs):
            print request.POST
            self.object = None
            self.item = get_object_or_404(self.item_class, pk=int(args[0]))
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            setattr(form.instance, self.item_class.__name__.lower(), self.item)

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        def form_invalid(self, form):
            data = [{'error': [unicode(f) + ': ' + ' '.join([unicode(i) for i in e]) for f, e in form.errors.items()]}]

            response = JSONResponse(data, {}, "application/json")
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response

        def form_valid(self, form):
            self.object = form.save()
            f = self.request.FILES.get('image')
            data = [{
                        'name': ' ',
                        'url': settings.MEDIA_URL + str(self.object.image),
                        'thumbnail_url': thumbnail(str(self.object.image), size='200;200'),
                        'delete_url': reverse('admin:' + self.delete_url_prefix, args=[getattr(self.object, self.item_class.__name__.lower()).id]) + 'delete/' + str(self.object.pk) + '/',
                        'delete_type': "DELETE"}]
            response = JSONResponse(data, {}, "application/json")
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response

    class ImagesDeleteView(DeleteView):

        def delete(self, request, *args, **kwargs):
            """удаление файлов"""

            self.object = self.get_object()
            #физическое удаление файлов с диска
            import os, glob
            img_file = os.path.join(settings.MEDIA_ROOT, unicode(self.object.image))

            files = glob.glob(os.path.join(os.path.dirname(img_file), (lambda n, e: n + '*.' + e)(*os.path.basename(img_file).split('.'))))

            for file in files: os.remove(file)

            self.object.delete()
            response = JSONResponse(True, {}, "application/json")
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response

