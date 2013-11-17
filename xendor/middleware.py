# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from xendor.settings import XendorSettings


class CmsCoreMiddleware(object):
    """closing site for  XENDOR_TEST_MODE=True"""
    def process_request(self, request):

        if settings.XENDOR_TEST_MODE and request.META['PATH_INFO'].find('/admin/') is -1:
            if not request.user.is_staff and not request.META['PATH_INFO'] == reverse('xendor-closed'):
                return HttpResponseRedirect(reverse('xendor-closed'))
        elif request.META['PATH_INFO'] == reverse('xendor-closed'):
            return HttpResponseRedirect(reverse('main-page'))


class XendorSettingMiddleware(object):
    """middleware for setting correct working"""

    def process_request(self, request):
        XendorSettings().clear_meta()

    def process_response(self, request, response):
        return response