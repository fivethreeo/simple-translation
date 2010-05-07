from django import template
from django.db import models
from simple_translation.translation_pool import translation_pool

register = template.Library()

def annotate_with_translations(object_or_list):
    if isinstance(object_or_list, models.Model):
        if hasattr(object_or_list, 'translations'):
            return object_or_list
    else:
        if hasattr(object_or_list[0], 'translations'):
            return object_or_list
    return translation_pool.annotate_with_translations(object_or_list)
register.filter(annotate_with_translations)

def get_preferred_translation_from_request(obj, request):
    from cms.utils import get_language_from_request
    language = get_language_from_request(request)
    if not hasattr(obj, 'translations'):
        annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation
register.filter(get_preferred_translation_from_request)
    
    
def get_preferred_translation_from_lang(obj, language):
    if not hasattr(obj, 'translations'):
        annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation    
register.filter(get_preferred_translation_from_lang)
    
    