from django.conf import settings
from django.contrib import admin
from django.forms.models import model_to_dict, fields_for_model, save_instance
from django import forms
from django.utils.safestring import mark_safe
import os
from cms.utils import get_language_from_request
from django.contrib.admin.views.main import ChangeList

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
    
    is_hidden = False
    button_js = '''
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
        
        buttons = []
        for lang in settings.LANGUAGES:
            button_classes = u'class="language_button%s"' % (lang[0] == value and ' selected' or '')
            buttons.append(u'''%s<input onclick="trigger_lang_button(this,'./?language=%s');"%s id="debutton" name="%s" value="%s" type="button">''' % (
                self.button_js, lang[0], button_classes, lang[0], lang[1]))
            
        tabs = """%s<div id="page_form_lang_tabs">%s</div>""" % (hidden_input, u''.join(buttons))

        return mark_safe(tabs)
    
class TranslationAdmin(PlaceholderAdmin):
    
    translation_model_language = 'language'

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
                
        
        form.base_fields['language'].widget = LanguageWidget()
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