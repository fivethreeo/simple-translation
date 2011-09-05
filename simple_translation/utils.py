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
    
def get_translation_filter(model, **kwargs):
    info = translation_pool.get_info(model)
    join_filter = info.translation_join_filter
    filter_dict = {}
    for key, value in kwargs.items():
        filter_dict['%s__%s' % (join_filter, key)] = value
    return filter_dict
    
def get_translation_filter_language(model, language, **kwargs):
    info = translation_pool.get_info(model)
    kwargs[info.language_field] = language
    return get_translation_filter(model, **kwargs)        

def get_translation_manager(obj):
    info = translation_pool.get_info(obj.__class__)
    return getattr(obj, info.translations_of_accessor)

def get_translation_queryset(obj):
    return get_translation_manager(obj).all()  

def get_translated_model(model):
    return translation_pool.get_info(model).translated_model   