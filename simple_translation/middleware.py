from django.conf import settings
from simple_translation.translation_pool import translation_pool

class MultilingualGenericsMiddleware:

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'queryset' in view_kwargs and translation_pool.is_registered(view_kwargs['queryset'].model):
            translation_info = translation_pool.get_info(view_kwargs['queryset'].model)
            filter_expr = '%s__%s' % (translation_info['translation_filter'], translation_info['language_field'])
            language = getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE)
            view_kwargs['queryset'] = view_kwargs['queryset'].filter(**{filter_expr: language}).distinct()
            

