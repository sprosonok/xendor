# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView

from xendor.models import Page
from xendor.structure import Structure


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        try:
            page = Page.objects.get(is_main=True)
        except Page.DoesNotExist:
            page = None

        context.update({
            'page': page
        })

        return context


class SiteMapView(TemplateView):
    template_name = 'sitemap.html'


class PageView(DetailView):
    model = Page
    template_name = 'page.html'

    def render_to_response(self, context, **response_kwargs):

        try:
            if self.get_object().app_extension:
                return HttpResponseRedirect(Structure().apps[self.get_object().app_extension]['node_url']())
        except:
            pass

        return super(PageView, self).render_to_response(context, **response_kwargs)
    
    def get_template_names(self):
        if self.get_object().template:
            return [self.get_object().template,]
        
        return DetailView.get_template_names(self)
    
    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        
        context.update({
            'page_address': unicode('parent=xendor-page&') + self.get_object().slug,
            'photo': 'uploads/about/r_tonel.jpg'
        })

        return context


class CloseView(TemplateView):
    template_name = 'close.html'

