# -*- coding: utf-8 -*-
from django.conf.urls import *

from xendor.views import PageView, HomeView, SiteMapView, CloseView

urlpatterns = patterns('',
    #главная страничка
    url(r'^$', HomeView.as_view(), name='xendor-home'),

    #карта сайта
    url(r'^sitemap/$', SiteMapView.as_view(), name="xendor-sitemap"),

    #Обработчик закрытого в целях тестирования сайта
    url(r'^xdp-closed/$', CloseView.as_view(), name="xendor-closed"),

    #странички цмс
    url(r'^(?P<slug>[\w/-]+)/$', PageView.as_view(), name="xendor-page"),
)
