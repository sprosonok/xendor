# -*- coding: utf-8 -*-
# Django settings for {{ project_name }} project.
import os, sys

NEED_REGENERATE_MODELS = ['Page',]
XDP_TEST_MODE = False #site closing

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'sprosonok@gmail.com'),
    ('tahy', 'tahy.gm@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '{{ project_name }}',          # Or path to database file if using sqlite3.
        'USER': 'root',                        # Not used with sqlite3.
        'PASSWORD': 'RewyM6',                  # Not used with sqlite3.
        'HOST': '85.12.240.187',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                        # Set to empty string for default. Not used with sqlite3.
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    }
}

SITE_URL = '127.0.0.1'
TIME_ZONE = 'Asia/Yekaterinburg'
LANGUAGE_CODE = 'ru-RU'
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = True


MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'public', 'media/').replace('\\','/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'public', 'static').replace('\\','/')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(__file__), 'static').replace('\\','/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '{{ secret_key }}'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "django.core.context_processors.csrf",
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    #site settings
    'xendor.middleware.XendorSettingMiddleware',
    'xendor.middleware.CmsCoreMiddleware',

    # site middleware
    '{{ project_name }}.middleware.SiteMiddleware',
)

ROOT_URLCONF = '{{ project_name }}.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '{{ project_name }}.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'xdp_admin',
    'django.contrib.sitemaps',

    ###===collection modules===###
    'supercaptcha',
    'south',

    #tree processing
    'mptt',
    'mpttadmin',

    #js-editor
    'tinymce',

    #CMS kernel
    'xendor',
    'filebrowser',

    ###===clients modules===###
)

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TINYMCE_DEFAULT_CONFIG = {
    'plugins' : "safari,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
    'theme': "advanced",
    'theme_advanced_buttons1' : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,|,styleselect,formatselect",
    'theme_advanced_buttons2' : "cut,copy,paste,pasteword,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,code,|,forecolor,backcolor",
    'theme_advanced_buttons3' : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,iespell,media,advhr,|,fullscreen",
    'theme_advanced_toolbar_location' : "top",
    'theme_advanced_toolbar_align' : "left",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_resizing' : "true",
    'relative_urls' : False,
}

MULTILANGUAL = SHOW_CHUNK_CATEGORIES = False

sys.path.append(os.path.join('c:\\distr','lib'))
sys.path.append(os.path.join('/home/tahy/workspace/development/python/libs','lib'))
sys.path.append(os.path.join('/Users/tahy/workspace/','lib'))