# -*- coding: utf-8 -*-
from django import forms
from django.forms.forms import BoundField
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from xendor.structure import Structure
from xendor.models import Page
from xendor.utils import cyr2lat


# ##===Страницы(Page)===###
app_choises = Structure().apps
choice_list = [['', ' - Модули не ассоциированы - ']]

for item in app_choises:
    choice_list.append([item, app_choises[item]['app_name']])


def get_children(node):
    list = []
    for item in node.get_children():
        list.append([item.id, (item.level + 1) * '--' + ' ' + item.title])
        list += get_children(item)

    return list


def get_pages():
    list = [[None, ' - Корень - '], ]
    for item in Page.objects.filter(level=0):
        list.append([item.id, (item.level + 1) * '--' + ' ' + item.title])
        list += get_children(item)

    return list


class PageAdminForm(forms.ModelForm):
    app_extension = forms.CharField(
        label='Ассоциированый модуль',
        required=False,
        widget=forms.Select(choices=choice_list),
    )

    parent = forms.ChoiceField(label=u'Родительский элемент', required=False)

    def __init__(self, *args, **kwargs):
        self.declared_fields['parent'].choices = get_pages()

        super(PageAdminForm, self).__init__(*args, **kwargs)


    # def clean_slug(self):
    #     slug = self.cleaned_data.get('slug', None)
    #
    #     if slug.lower() != cyr2lat(slug).lower().replace(' ', '_'):
    #         raise forms.ValidationError(u'Неправильный формат синонима страницы (нельзя использовать дефис)')
    #
    #     return slug

    def clean_parent(self):
        parent = self.cleaned_data.get('parent', None)

        try:
            parent = Page.objects.get(pk=parent)
        except:
            parent = None

        if parent and self.instance.id:
            children = [[self.instance.id,
                         (self.instance.level + 1) * '—' + ' ' + self.instance.title], ] + get_children(self.instance)

            if [parent.id, (parent.level + 1) * '——' + ' ' + parent.title] in children:
                raise forms.ValidationError(u'Страница не может быть дочерней к себе или своим потомкам')

        return parent

    class Meta:
        model = Page

        exclude = (
        )
