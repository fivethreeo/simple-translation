from django.conf import settings
from django import template
from django.template.loader import render_to_string
from django.db import models
from simple_translation.translation_pool import translation_pool

register = template.Library()

def annotate_with_translations(object_or_list):
    return translation_pool.annotate_with_translations(object_or_list)
register.filter(annotate_with_translations)

def get_preferred_translation_from_request(obj, request):
    language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    if not hasattr(obj, 'translations'):
        annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation
    return obj.translations[0]    
register.filter(get_preferred_translation_from_request)
    
def get_preferred_translation_from_lang(obj, language):
    if not hasattr(obj, 'translations'):
        annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation
    return obj.translations[0]
register.filter(get_preferred_translation_from_lang)
    
def render_language_choices(obj, request):
    if not hasattr(obj, 'translations'):
        annotate_with_translations(obj)
    language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    translations = [translation for translation in obj.translations if translation.language != language]
    opts = obj.__class__._meta
    app_label = opts.app_label
    return render_to_string([
        'simple_translation/%s/%s/language_choices.html' % (app_label, opts.object_name.lower()),
        'simple_translation/%s/language_choices.html' % app_label,
        'simple_translation/language_choices.html'
    ], {'translations': translations})
register.filter(render_language_choices)
        
