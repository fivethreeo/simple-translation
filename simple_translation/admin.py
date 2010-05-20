from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib import admin
from django.forms.models import model_to_dict, fields_for_model, save_instance
from django import forms
from django.utils.safestring import mark_safe
import os
from cms.utils import get_language_from_request
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.util import unquote, get_deleted_objects
from django.utils.text import capfirst
from django.utils.encoding import force_unicode
from django.http import HttpResponseRedirect, HttpResponse, Http404, \
    HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from cms.admin.placeholderadmin import PlaceholderAdmin

"""
Example usage:

models.py

from django.db import models
from cms import settings

class Entry(models.Model):
    published = models.BooleanField()

class EntryTitle(models.Model):
    entry = models.ForeignKey(BlogEntry)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255)

admin.py

from django.contrib import admin
from models import Entry, EntryTitle

class EntryAdmin(TranslationAdmin):

    translation_model = EntryTitle
    translation_model_fk = 'entry'

admin.site.register(Entry, EntryAdmin)
"""        


class LanguageChangeList(ChangeList):

    def get_results(self, request):
        super(LanguageChangeList, self).get_results(request)
        from simple_translation.translation_pool import translation_pool
        self.result_list = translation_pool.annotate_with_translations(self.result_list)
        self.can_show_all = False


class LanguageWidget(forms.HiddenInput):
    
    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop('translation')
        super(LanguageWidget, self).__init__(*args, **kwargs)
            
    is_hidden = False
    button_js = u'''
    <script type="text/javascript">
    
    $(document).ready(function () {
        $("#id_slug").change(function() { this._changed = true; });
        $('#id_title').change(function() {this._changed = true; });
    })  
    
    trigger_lang_button = function(e, url) {
        // also make sure that we will display the confirm dialog
        // in case users switch tabs while editing plugins
        changed = false;
        if($("#id_slug")[0]._changed){
            changed = true;
        }

        if($("#id_title")[0]._changed){
            changed = true;
        }

        if($('iframe').length){
            changed = true;
        }

        if (changed) {
            var question = gettext("Are you sure you want to change tabs without saving the page first?")
            var answer = confirm(question);
        }else{
            var answer = true;
        }

        if (!answer) {
            return false;
        } else {
            window.location = url;
        }
    }
  
    </script>
    '''
    
    def render(self, name, value, attrs=None):
        
        hidden_input = super(LanguageWidget, self).render(name, value, attrs=attrs)
        lang_dict = dict(settings.LANGUAGES)
        
        buttons = []
        for lang in settings.LANGUAGES:
            button_classes = u'class="language_button%s"' % (lang[0] == value and ' selected' or '')
            buttons.append(u''' <input onclick="trigger_lang_button(this,'./?language=%s');"%s id="debutton" name="%s" value="%s" type="button">''' % (
                lang[0], button_classes, lang[0], lang[1]))
                
        lang_descr = u'Delete: &quot;%s&quot; translation.' % force_unicode(lang_dict[str(value)]) 
        if self.translation.pk:
            buttons.append(u'''&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input onclick="trigger_lang_button(this,'delete-translation/?language=%s');"%s id="debutton" name="%s" value="%s" type="button">''' % (
                    value, u'', 'dellang', lang_descr ))    
                
        tabs = u"""%s%s<div id="page_form_lang_tabs">%s</div>""" % (self.button_js, hidden_input, u''.join(buttons))

        return mark_safe(tabs)
    
class TranslationAdmin(PlaceholderAdmin):
    
    list_display = ('description', 'languages')
    
    def __init__(self, *args, **kwargs):
        super(TranslationAdmin, self).__init__(*args, **kwargs)
        from simple_translation.translation_pool import translation_pool
        translation_info = translation_pool.get_info(self.model)
        self.translation_model = translation_info['model']
        self.translation_model_fk = translation_info['translation_model_fk']
        self.translation_model_language = translation_info['language_field']

    def description(self, obj):
        return hasattr(obj, 'translations') and unicode(obj.translations[0]) or u'No translations'
    
    def languages(self, obj):
            lnk = '<a href="%s/?language=%s">%s</a>'
            trans_list = [ (obj.pk,  getattr(t, self.translation_model_language), getattr(t, self.translation_model_language).upper())
                for t in getattr(obj, 'translations', []) ]
            return ' '.join([lnk % t for t in trans_list])
    languages.short_description = 'Languages'
    languages.allow_tags = True

    def get_changelist(self, request, **kwargs):
        return LanguageChangeList
        
    def get_translation(self, request, obj):

        language = get_language_from_request(request)

        if obj:
            
            get_kwargs = {
                self.translation_model_fk: obj,
                self.translation_model_language: language
            }

            try:
                return self.translation_model.objects.get(**get_kwargs)
            except:
                return self.translation_model(**get_kwargs)

        return self.translation_model(**{self.translation_model_language: language})

    def get_form(self, request, obj=None, **kwargs):

        form = super(TranslationAdmin, self).get_form(request, obj, **kwargs)

        add_fields = fields_for_model(self.translation_model, exclude=[self.translation_model_fk])

        translation_obj = self.get_translation(request, obj)
        initial = model_to_dict(translation_obj)

        for name, field in add_fields.items():
            form.base_fields[name] = field
            if name in initial:
                form.base_fields[name].initial = initial[name]
                
        
        form.base_fields['language'].widget = LanguageWidget(translation=translation_obj)
        return form

    def save_model(self, request, obj, form, change):
        super(TranslationAdmin, self).save_model(request, obj, form, change)
        
        translation_obj = self.get_translation(request, obj)
        translation_obj = save_instance(form, translation_obj, commit=False)
        
        setattr(translation_obj, self.translation_model_fk, obj) 
        
        translation_obj.save()
        
    def placeholder_plugin_filter(self, request, queryset):
        language = get_language_from_request(request)
        return queryset.filter(language=language)
        
    def response_change(self, request, obj):
        response = super(TranslationAdmin, self).response_change(request, obj)
        language = get_language_from_request(request)
        if response.status_code == 302 and response._headers['location'][1] == request.path:
            location = response._headers['location']
            response._headers['location'] = (location[0], "%s?language=%s" % (location[1], language))
        return response
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        response = super(TranslationAdmin, self).response_add(request, obj, post_url_continue)
        if request.POST.has_key("_continue"):
            language = get_language_from_request(request)
            location = response._headers['location']
            response._headers['location'] = (location[0], "%s?language=%s" % (location[1], language))
        return response
        
    def delete_translation(self, request, object_id, extra_context=None):
        from simple_translation.translation_pool import translation_pool

        language = get_language_from_request(request)

        opts = self.model._meta
        translationopts = self.translation_model._meta
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

        translationobj = get_object_or_404(self.translation_model, **{self.translation_model_fk + '__id': object_id, 'language': language})
        
        deleted_objects, perms_needed = get_deleted_objects([translationobj], translationopts, request.user, self.admin_site)        

        if request.method == 'POST':
            if perms_needed:
                raise PermissionDenied

            message = _('%(obj_name)s with language %(language)s was deleted') % {
                'language': [name for code, name in settings.CMS_LANGUAGES if code == language][0], 'obj_name': force_unicode(translationopts.verbose_name)}
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
            return super(TranslationAdmin, self).render_change_form(request, context, True, change,  form_url, obj)
        else:
            return super(TranslationAdmin, self).render_change_form(request, context, add, change,  form_url, obj)
            
    def get_urls(self):
        """Get the admin urls"""
        from django.conf.urls.defaults import patterns, url
        info = "%s_%s" % (self.model._meta.app_label, self.model._meta.module_name)
        pat = lambda regex, fn: url(regex, self.admin_site.admin_view(fn), name='%s_%s' % (info, fn.__name__))

        url_patterns = patterns('',
            pat(r'^([0-9]+)/delete-translation/$', self.delete_translation),
        )

        url_patterns = url_patterns + super(TranslationAdmin, self).get_urls()
        return url_patterns

