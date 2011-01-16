from django.conf import settings
from simple_translation.translation_pool import translation_pool

class MultilingualGenericsMiddleware:

    def process_view(self, request, view_func, view_args, view_kwargs):
        
        language = None
        if 'language_code' in view_kwargs:
            language = view_kwargs.pop('language_code')
            
        if not language and 'django.middleware.locale.LocaleMiddleware' in settings.MIDDLEWARE_CLASSES:
            language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
        if language:
            if 'queryset' in view_kwargs:
                if translation_pool.is_registered(view_kwargs['queryset'].model):
                    translation_info = translation_pool.get_info(view_kwargs['queryset'].model)
                    filter_expr = '%s_%s' % (['translation_filter'], translation_info['language_field'])
                if translation_pool.is_registered_translation(view_kwargs['queryset'].model):
                    translation_info = translation_pool.get_info(view_kwargs['queryset'].model)
                    filter_expr = '%s' % translation_info['language_field']
                if filter_expr:
                    view_kwargs['queryset'] = view_kwargs['queryset'].filter(**{filter_expr: language}).distinct()
                

