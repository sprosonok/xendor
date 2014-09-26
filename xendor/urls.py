# -*- coding: utf-8 -*-
from django.conf.urls import *

from xendor.views import PageView, HomeView, CloseView

urlpatterns = patterns('',
    #главная страничка
    url(r'^$', HomeView.as_view(), name='xendor-home'),

    #Обработчик закрытого в целях тестирования сайта
    url(r'^xendor-closed/$', CloseView.as_view(), name="xendor-closed"),

    #странички цмс
    url(r'^(?P<slug>[\w/-]+)/$', PageView.as_view(), name="xendor-page"),
)
