# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User

class SiteMiddleware(object):
    def process_request (self, request):
        if not settings.SITE_URL in request.META.get('HTTP_REFERER', []):
            request.session['user_referer'] = unicode(request.META.get('HTTP_REFERER', ''))

    def process_response(self, request, response):
        return response