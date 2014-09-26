# -*- coding: utf-8 -*-
# from django.utils.translation import ugettext as _
#
# from mpttadmin import editor
# from mptt.forms import MPTTAdminForm
#
#
# class XDP17TreeModelAdmin(editor.TreeEditor):
#     """
#     A ModelAdmin to add changelist tree view and editing capabilities.
#     Requires FeinCMS to be installed.
#     """
#
#     form = MPTTAdminForm
#
#     def _actions_column(self, obj):
#         actions = super(XDP17TreeModelAdmin, self)._actions_column(obj)
#         actions.insert(0,
#             u'<a href="add/?%s=%s" title="%s"><img src="/static/admin/img/icon_addlink.gif" alt="%s" /></a>' % (
#                 self.model._mptt_meta.parent_attr,
#                 obj.pk,
#                 _('Add child'),
#                 _('Add child')))
#
#         if hasattr(obj, 'get_absolute_url'):
#             actions.insert(0,
#                 u'<a href="%s" title="%s" target="_blank"><img src="/static/admin/img/selector-search.gif" alt="%s" /></a>' % (
#                     obj.get_absolute_url(),
#                     _('View on site'),
#                     _('View on site')))
#         return actions
#
#     def delete_selected_tree(self, modeladmin, request, queryset):
#         """
#         Deletes multiple instances and makes sure the MPTT fields get recalculated properly.
#         (Because merely doing a bulk delete doesn't trigger the post_delete hooks.)
#         """
#         n = 0
#         for obj in queryset:
#             obj.delete()
#             n += 1
#         self.message_user(request, _("Successfully deleted %s items." % n))
#
#     def get_actions(self, request):
#         actions = super(XDP17TreeModelAdmin, self).get_actions(request)
#         if 'delete_selected' in actions:
#             actions['delete_selected'] = (self.delete_selected_tree, 'delete_selected', _("Delete selected %(verbose_name_plural)s"))
#         return actions
