# -*- coding: utf-8 -*-

def _formater_1000(value):
    """Форматирование больших чисел в более читабельный вид"""
    try:
        if not '.' in value:
            value = value + '.0'
        return (lambda h, q:
                (lambda s:
                 ''.join(reversed(['&nbsp;' * int(not((i + 1) % 3) and i != 0) + s[len(s) - i - 1] for i in xrange(len(s))]))
                    )(h) + ('.' + str(round(float('.' + q), 2)).split('.')[1]) * int(bool(int(q)))
            )(*str(value).split('.')).lstrip('&nbsp;')
    except:
        return value
    
uploader_js = """
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-upload fade">
        <td class="preview"><span class="fade"></span></td>
        <td class="name"><span>{%=file.name%}</span></td>
        <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
        {% if (file.error) { %}
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else if (o.files.valid && !i) { %}
            <td>
                <div class="progress progress-success progress-striped active"><div class="bar" style="width:0%;"></div></div>
            </td>
            <td class="start">{% if (!o.options.autoUpload) { %}
                <button class="btn btn-success">
                    <i class="icon-upload icon-white"></i>
                    <span>{%=locale.fileupload.start%}</span>
                </button>
            {% } %}</td>
        {% } else { %}
            <td colspan="2"></td>
        {% } %}
        <td class="cancel">{% if (!i) { %}
            <button class="btn btn-warning">
                <i class="icon-ban-circle icon-white"></i>
                <span>{%=locale.fileupload.cancel%}</span>
            </button>
        {% } %}</td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-download fade">
        {% if (file.error) { %}
            <td></td>
            <td class="name"><span>{%=file.name%}</span></td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td class="error" colspan="2"><span class="label label-important">{%=locale.fileupload.error%}</span> {%=locale.fileupload.errors[file.error] || file.error%}</td>
        {% } else { %}
            <td class="preview">{% if (file.thumbnail_url) { %}
                <a href="{%=file.url%}" title="{%=file.name%}" rel="gallery" download="{%=file.name%}"><img src="{%=file.thumbnail_url%}"></a>
            {% } %}</td>
            <td class="name">
                <a href="{%=file.url%}" title="{%=file.name%}" rel="{%=file.thumbnail_url&&'gallery'%}" download="{%=file.name%}">{%=file.name%}</a>
            </td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td colspan="2"></td>
        {% } %}
        <td class="delete">
            <button class="btn btn-danger" data-type="{%=file.delete_type%}" data-url="{%=file.delete_url%}">
                <i class="icon-trash icon-white"></i>
                <span>{%=locale.fileupload.destroy%}</span>
            </button>
            <input type="checkbox" name="delete" value="1">
        </td>
    </tr>
{% } %}
</script>
"""

from django.conf import settings
from django.db.models import Q, get_model

def get_completed():
    count, all = 0, 0
    
    for model_name, options in settings.CONTENT_MODELS.items():
        assert 'fields' in options, \
               'Please, set up fields options for "%s".' % modelname
        
        fields = options['fields']
        trigger = options.get('trigger', None)
        
        app_label, model_name = model_name.split('.')
        model = get_model(app_label, model_name)
        
        search_lookup = None

        for field in fields:
            if '|' in field:
                pass
            elif search_lookup is None:
                search_lookup = Q(**{field: None})
                search_lookup |= Q(**{field: ''})
            else:
                search_lookup |= Q(**{field: None})
                search_lookup |= Q(**{field: ''})
        
        objects = model.objects.all().exclude(search_lookup).distinct()
        
        if trigger:
            for obj in objects:
                if not trigger(obj):
                    continue            
                count += 1
        else:
            count = objects.count()
        
        all += model.objects.all().count()
    
    return count, all, int(100.0*count/all)

