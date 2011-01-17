from django.conf import settings
from django.middleware.locale import LocaleMiddleware
from django.utils import translation

from simple_translation.translation_pool import translation_pool

class MultilingualGenericsMiddleware(LocaleMiddleware):
    
    language_fallback_middlewares = ['django.middleware.locale.LocaleMiddleware']
    
    def has_language_fallback_middlewares(self):
        has_fallback = False
        for middleware in self.language_fallback_middlewares: 
            if middleware in settings.MIDDLEWARE_CLASSES:
                has_fallback = True
        return has_fallback
        
    def process_request(self, request):
 	    pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        language = None
        if 'language_code' in view_kwargs:
            # get language and set tralslation
            language = view_kwargs.pop('language_code')
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()
            
        if not language:
            if not self.has_language_fallback_middlewares():
                super(MultilingualGenericsMiddleware, self).process_request(request)
            language = getattr(request, 'LANGUAGE_CODE')
            
        if 'queryset' in view_kwargs:
            if translation_pool.is_registered(view_kwargs['queryset'].model):
                translation_info = translation_pool.get_info(view_kwargs['queryset'].model)
                filter_expr = '%s__%s' % (translation_info['translation_filter'], translation_info['language_field'])
            if translation_pool.is_registered_translation(view_kwargs['queryset'].model):
                translation_info = translation_pool.get_info(view_kwargs['queryset'].model)
                filter_expr = '%s' % translation_info['language_field']
            if filter_expr:
                view_kwargs['queryset'] = view_kwargs['queryset'].filter(**{filter_expr: language}).distinct()
                    
    def process_response(self, request, response):
        if not 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE_CLASSES:
            return super(MultilingualGenericsMiddleware, self).process_response(request, response)
        return response