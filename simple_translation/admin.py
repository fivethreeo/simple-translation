import os

from django.utils.translation import ugettext as _

from django.conf import settings
from django.db import router
from django.contrib import admin

from django.contrib.admin.util import unquote, get_deleted_objects, flatten_fieldsets

from django.utils.encoding import force_unicode
from django.utils.functional import curry
from django.http import HttpResponseRedirect, HttpResponse, Http404, \
    HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from simple_translation.widgets import LanguageWidget
from simple_translation.forms import TranslationModelForm, translation_modelform_factory
from simple_translation.utils import get_language_from_request
from simple_translation.translation_pool import translation_pool

def make_translation_admin(admin):
    
    class RealTranslationAdmin(admin):
        
        form = TranslationModelForm
        
        list_display = ('description', 'languages')
        
        def __init__(self, *args, **kwargs):
            super(RealTranslationAdmin, self).__init__(*args, **kwargs)
            info = translation_pool.get_info(self.model)
            self.translated_model = info.translated_model
            self.translation_of_field = info.translation_of_field
            self.language_field = info.language_field
    
        def description(self, obj):
            return getattr(translation_pool.annotate_with_translations(obj), 'translations', []) \
            	and unicode(translation_pool.annotate_with_translations(obj).translations[0]) or u'No translations'
        
        def languages(self, obj):
                lnk = '<a href="%s/?language=%s">%s</a>'
                trans_list = [ (obj.pk, \
                	getattr(t, self.language_field), getattr(t, self.language_field).upper())
                    	for t in getattr(translation_pool.annotate_with_translations(obj), 'translations') or []]
                return ' '.join([lnk % t for t in trans_list])
        languages.short_description = 'Languages'
        languages.allow_tags = True

        def get_translation(self, request, obj):
    
            language = get_language_from_request(request)
 
            if obj:
                
                get_kwargs = {
                    self.translation_of_field: obj,
                    self.language_field: language
                }
    
                try:
                    return self.translated_model.objects.get(**get_kwargs)
                except:
                    return self.translated_model(**get_kwargs)
    
            return self.translated_model(**{self.language_field: language})
                
        def get_form(self, request, obj=None, **kwargs):
            """
            Returns a Form class for use in the admin add view. This is used by
            add_view and change_view.
            """
            if self.declared_fieldsets:
                fields = flatten_fieldsets(self.declared_fieldsets)
            else:
                fields = None
            if self.exclude is None:
                exclude = []
            else:
                exclude = list(self.exclude)
            exclude.extend(kwargs.get("exclude", []))
            exclude.extend(self.get_readonly_fields(request, obj))
            # if exclude is an empty list we pass None to be consistant with the
            # default on modelform_factory
            exclude = exclude or None
            defaults = {
                "form": self.form,
                "fields": fields,
                "exclude": exclude,
                "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            }
            defaults.update(kwargs)
            new_form = translation_modelform_factory(self.model, **defaults)
            current_language = get_language_from_request(request)
            translation_obj = self.get_translation(request, obj)
            new_form.base_fields[self.language_field].widget = LanguageWidget(
            	translation_of_obj=obj,
            	translation_obj=translation_obj
            )
            new_form.base_fields[self.language_field].initial = current_language

            return new_form
            
        def save_translated_form(self, request, obj, form, change):
            return form.child_form.save(commit=False)            

        def save_translated_model(self, request, obj, translation_obj, form, change):
            setattr(translation_obj, self.translation_of_field, obj) 
            translation_obj.save()
            
        def save_model(self, request, obj, form, change):
            super(RealTranslationAdmin, self).save_model(request, obj, form, change)
            translation_obj = self.save_translated_form(request, obj, form, change)
            self.save_translated_model(request, obj, translation_obj, form, change)
            
        def placeholder_plugin_filter(self, request, queryset):
            language = get_language_from_request(request)
            return queryset.filter(language=language)
            
        def response_change(self, request, obj):
            response = super(RealTranslationAdmin, self).response_change(request, obj)
            language = get_language_from_request(request)
            if response.status_code == 302 and response._headers['location'][1] == request.path:
                location = response._headers['location']
                response._headers['location'] = (location[0], "%s?language=%s" % (location[1], language))
            return response
        
        def response_add(self, request, obj, post_url_continue='../%s/'):
            response = super(RealTranslationAdmin, self).response_add(request, obj, post_url_continue)
            if request.POST.has_key("_continue"):
                language = get_language_from_request(request)
                location = response._headers['location']
                response._headers['location'] = (location[0], "%s?language=%s" % (location[1], language))
            return response
            
        def delete_translation(self, request, object_id, extra_context=None):
    
            language = get_language_from_request(request)
 
            opts = self.model._meta
            translationopts = self.translated_model._meta
            app_label = translationopts.app_label
    
            try:
                obj = self.queryset(request).get(pk=unquote(object_id))
            except self.model.DoesNotExist:
                # Don't raise Http404 just yet, because we haven't checked
                # permissions yet. We don't want an unauthenticated user to be able
                # to determine whether a given object exists.
                obj = None
    
            if not self.has_delete_permission(request, obj):
                raise PermissionDenied
    
            if obj is None:
                raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})
    
            if not len(translation_pool.annotate_with_translations(obj).translations) > 1:
                raise Http404(_('There only exists one translation for this page'))
    
            translationobj = get_object_or_404(self.translated_model, **{self.translation_of_field + '__id': object_id, 'language': language})
            using = router.db_for_write(self.model)
            deleted_objects, perms_needed = get_deleted_objects([translationobj], translationopts, request.user, self.admin_site, using)        
    
            if request.method == 'POST':
                if perms_needed:
                    raise PermissionDenied
    
                message = _('%(obj_name)s with language %(language)s was deleted') % {
                    'language': [name for code, name in settings.LANGUAGES if code == language][0], 'obj_name': force_unicode(translationopts.verbose_name)}
                self.log_change(request, translationobj, message)
                self.message_user(request, message)
    
                translationobj.delete()
    
                if not self.has_change_permission(request, None):
                    return HttpResponseRedirect("../../../../")
                return HttpResponseRedirect("../../")
    
            context = {
                "title": _("Are you sure?"),
                "object_name": force_unicode(translationopts.verbose_name),
                "object": translationobj,
                "deleted_objects": deleted_objects,
                "perms_lacking": perms_needed,
                "opts": translationopts,
                "root_path": self.admin_site.root_path,
                "app_label": app_label,
            }
            context.update(extra_context or {})
            context_instance = RequestContext(request, current_app=self.admin_site.name)
            return render_to_response(self.delete_confirmation_template or [
                "admin/%s/%s/delete_confirmation.html" % (app_label, translationopts.object_name.lower()),
                "admin/%s/delete_confirmation.html" % app_label,
                "admin/delete_confirmation.html"
            ], context, context_instance=context_instance)
            
        def render_change_form(self, request, context, add=False, change=False,  form_url='', obj=None):
            if not self.get_translation(request, obj).pk:
                return super(RealTranslationAdmin, self).render_change_form(request, context, True, change,  form_url, obj)
            else:
                return super(RealTranslationAdmin, self).render_change_form(request, context, add, change,  form_url, obj)
                
        def get_urls(self):
            """Get the admin urls"""
            from django.conf.urls.defaults import patterns, url
            info = "%s_%s" % (self.model._meta.app_label, self.model._meta.module_name)
            pat = lambda regex, fn: url(regex, self.admin_site.admin_view(fn), name='%s_%s' % (info, fn.__name__))
    
            url_patterns = patterns('',
                pat(r'^([0-9]+)/delete-translation/$', self.delete_translation),
            )
    
            url_patterns = url_patterns + super(RealTranslationAdmin, self).get_urls()
            return url_patterns
    return RealTranslationAdmin
    
TranslationAdmin = make_translation_admin(admin.ModelAdmin)

if 'cms' in settings.INSTALLED_APPS:
    from cms.admin.placeholderadmin import PlaceholderAdmin
    PlaceholderTranslationAdmin = make_translation_admin(PlaceholderAdmin)



