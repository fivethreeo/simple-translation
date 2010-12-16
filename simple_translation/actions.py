from django.conf import settings
from cms.utils.placeholder import PlaceholderNoAction
from cms.models import CMSPlugin

LANG_DICT = dict(settings.LANGUAGES)

class SimpleTranslationPlaceholderActions(PlaceholderNoAction):
    can_copy = True

    def copy(self, target_placeholder, source_language, fieldname, model, target_language, **kwargs):

        plugins = list(target_placeholder.get_plugins().filter(language=source_language))
        ptree = []
        new_plugins = []
        for p in plugins:
            new_plugins.append(p.copy_plugin(target_placeholder, target_language, ptree))
        return new_plugins
    
    def get_copy_languages(self, placeholder, model, fieldname, **kwargs):
        language_codes = CMSPlugin.objects.filter(placeholder=placeholder).distinct().values_list('language', flat=True)
        return [(lc, LANG_DICT.get(lc)) for lc in language_codes] 
