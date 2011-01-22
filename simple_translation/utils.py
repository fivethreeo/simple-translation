from django.conf import settings
from simple_translation.translation_pool import translation_pool

def get_language_from_request(request):
    return request.REQUEST.get('language', getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE))

def get_preferred_translation_from_request(obj, request):
    language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
    if not hasattr(obj, 'translations'):
        translation_pool.annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation
    return obj.translations[0]
    
def get_preferred_translation_from_lang(obj, language):
    if not hasattr(obj, 'translations'):
        translation_pool.annotate_with_translations(obj)
    for translation in obj.translations:
        if translation.language == language:
            return translation
    return obj.translations[0]