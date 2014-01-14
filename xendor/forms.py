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


###===Страницы(Page)===###
app_choises = Structure().apps
choice_list = [['', ' - Модули не ассоциированы - ']]

for item in app_choises:
    choice_list.append([item, app_choises[item]['app_name']])


def get_children(node):
    list = []
    for item in node.get_children():
        list.append([item.id, (item.level+1)*'--'+' '+item.title])
        list += get_children(item)

    return list

def get_pages():
    list = [[None, ' - Корень - '],]
    for item in Page.objects.filter(level=0):
        list.append([item.id, (item.level+1)*'--'+' '+item.title])
        list += get_children(item)

    return list


class PageAdminForm(forms.ModelForm):
    app_extension = forms.CharField(
        label = 'Ассоциированый модуль',
        required = False,
        widget = forms.Select( choices = choice_list ),
    )

    parent = forms.ChoiceField(label=_(u'Parent'), required = False)

    def __init__(self, *args, **kwargs):
        self.declared_fields['parent'].choices = get_pages()

        super(PageAdminForm, self).__init__ (*args, **kwargs)


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
        except :
            parent = None

        if parent and self.instance.id:
            children = [[self.instance.id, (self.instance.level+1)*'--'+' '+self.instance.title],] + get_children(self.instance)

            if [parent.id, (parent.level+1)*'--'+' '+parent.title] in children:
                raise forms.ValidationError(u'Страница не может быть дочерней к себе или своим потомкам')

        return parent

    class Meta:
        model = Page

        exclude = (
        )


def bootstrapped(self):
    """Вывод формы отформатированной в соотвествии со стилями бутстрапа.
       Осторожно!!! Ч0рная магия и запутанный код!
    """

    normal_row = u"""
        <div class="control-group %(has_error)s">
            %(label)s
            <div class="controls">
                %(field)s
                <span class="help-inline">%(errors)s</span>
                <p class="help-block">%(help_text)s</p>
            </div>
        </div>"""
    error_row = u'<li>%s</li>'
    row_ender = u'</div>'
    help_text_html = u' %s'

    top_errors = self.non_field_errors()
    output, hidden_fields = [], []

    for name, field in self.fields.items():
        html_class_attr = ''
        
        bf = BoundField(self, field, name)
        bf_errors = self.error_class([conditional_escape(error) for error in bf.errors])
        error_text = bf.errors.as_text()[2:]
        has_error = ''
        if error_text:
            has_error = ' error'

        if bf.is_hidden:
            if bf_errors:
                top_errors.extend([u'(Hidden field %s) %s' % (name, force_unicode(e)) for e in bf_errors])
            hidden_fields.append(unicode(bf))
        else:

            css_classes = bf.css_classes()
            if css_classes:
                html_class_attr = ' class="%s"' % css_classes

            if bf.label:
                label = conditional_escape(force_unicode(bf.label))

                if self.label_suffix:
                    if label[-1] not in ':?.!':
                        label += self.label_suffix
                label = bf.label_tag(label, attrs={'class': "control-label"}) or ''
            else:
                label = ''

            if field.help_text:
                help_text = help_text_html % force_unicode(field.help_text)
            else:
                help_text = u''
                
            output.append(normal_row % {
                'has_error': force_unicode(has_error),
                'errors': force_unicode(error_text),
                'label': force_unicode(label),
                'field': unicode(bf),
                'help_text': help_text,
                'html_class_attr': html_class_attr
            })

    if top_errors:
        output.insert(0, error_row % force_unicode(top_errors))

    if hidden_fields:
        str_hidden = u''.join(hidden_fields)
        if output:
            last_row = output[-1]

            if not last_row.endswith(row_ender):
                last_row = (normal_row % {'errors': '', 'label': '',
                                          'field': '', 'help_text':'', 'has_error': has_error,
                                          'html_class_attr': html_class_attr})
                output.append(last_row)
            output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
        else:
            output.append(str_hidden)
    return mark_safe(u'\n'.join(output))

forms.BaseForm.bootstrapped = bootstrapped
