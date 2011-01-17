from django.db import models
from django.conf import settings

class TranslationAllreadyRegistered(Exception):
    pass

class TranslationPool(object):
    
    discovered = False
    translated_models = {}
    translation_models = {}
    
    def discover_translations(self):        
        if self.discovered:
            return
        for app in settings.INSTALLED_APPS:
            __import__(app, {}, {}, ['simple_translate'])
        self.discovered = True    

    def get_info(self, model):
        self.discover_translations()
        if model in self.translated_models:
            return self.translated_models[model]
        elif model in self.translation_models:
            return self.translated_models[self.translation_models[model]]
        
    def register_translation(self, translation_of_model, translated_model, language_field='language'):
        
        assert issubclass(translation_of_model, models.Model) and issubclass(translated_model, models.Model)
        if translation_of_model in self.translated_models:
            raise TranslationAllreadyRegistered, "[%s] a translation for this model is already registered" % translation_of_model.__name__
            
        self.translated_models[translation_of_model] = {}
        self.translated_models[translation_of_model]['model'] = translated_model
        self.translation_models[translated_model] = translation_of_model
        
        opts = translation_of_model._meta
        for rel in opts.get_all_related_objects():
            if rel.model == translated_model:
                self.translated_models[translation_of_model]['translation_model_fk'] = rel.field.name
                self.translated_models[translation_of_model]['translation_accessor'] = rel.get_accessor_name()

        self.translated_models[translation_of_model]['translation_filter'] = translated_model.__name__.lower()          
        self.translated_models[translation_of_model]['language_field'] = language_field     
             
    def annotate_with_translations(self, list_or_instance):
        
        self.discover_translations()
        if not list_or_instance:
            return list_or_instance
        if isinstance(list_or_instance, models.Model):
            model = list_or_instance.__class__
            instance = list_or_instance
            if self.is_registered_translation(model):
                instance = getattr(list_or_instance, self.get_info(model)['translation_model_fk'])
            list_or_instance.translations = list(getattr(instance, \
            	self.get_info(model)['translation_accessor']).all())
            return list_or_instance
        else:
            result_list = list_or_instance
            if not len(result_list):
                return result_list
            model = list_or_instance[0].__class__
            
            info = self.get_info(model)
            translated_model = info['model']
            if self.is_registered_translation(model):
                translation_model_fk = self.translated_models[model]['translation_model_fk'] 
            else:
                translation_model_fk = self.translated_models[model]['translation_model_fk'] 
               
            id_list = [r.pk for r in result_list]
            pk_index_map = dict([(pk, index) for index, pk in enumerate(id_list)])
            
            translations = translated_model.objects.filter(**{
                translation_model_fk + '__in': id_list
            })
            
            for obj in translations:
                index = pk_index_map[getattr(obj, translation_model_fk + '_id')]
                if not hasattr(result_list[index], 'translations'):
                    result_list[index].translations = []
                result_list[index].translations.append(obj)
        
        return result_list
    
    def is_registered_translation(self, model):
        self.discover_translations()
        if model in self.translation_models:
            return True
        return False
        
    def is_registered(self, model):
        self.discover_translations()
        if model in self.translated_models:
            return True
        return False
            
translation_pool = TranslationPool()
