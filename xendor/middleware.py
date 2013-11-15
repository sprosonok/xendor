# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from xendor.settings import XendorSettings


class CmsCoreMiddleware(object):

    def process_request(self, request):
        if request.META['PATH_INFO'].find('.') is -1:
            if settings.XDP_TEST_MODE and request.META['PATH_INFO'].find('/admin/') is -1:
                if not request.user.is_staff and not request.META['PATH_INFO'] == reverse('xendor-closed'):
                    return HttpResponseRedirect(reverse('xendor-closed'))
            elif request.META['PATH_INFO'] == reverse('xendor-closed'):
                return HttpResponseRedirect(reverse('main-page'))


class XendorSettingMiddleware(object):

    def process_request(self, request):
        XendorSettings().clear_meta()

    def process_response(self, request, response):
        return response