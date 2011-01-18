from django.forms.models import model_to_dict, fields_for_model
from django.forms.models import BaseModelForm, ModelForm, ModelFormMetaclass, modelform_factory, model_to_dict
from django.forms.util import ErrorList

from simple_translation.translation_pool import translation_pool

class TranslationModelFormMetaclass(ModelFormMetaclass):
    
    def __new__(cls, name, bases, attrs):
        formfield_callback = attrs.get('formfield_callback', None)
        try:
            parents = [b for b in bases if issubclass(b, TranslationModelForm)]
        except NameError:
            # We are defining TranslationModelForm itself.
            parents = None
            
        new_class = super(TranslationModelFormMetaclass, cls).__new__(cls, name, bases,
                attrs)
        if not parents:
            return new_class
            
        opts = new_class._meta
        if opts.model:
            if translation_pool.is_registered(opts.model):
                info = translation_pool.get_info(opts.model)
                translation_model = info['model']
                new_class.child_form_class = modelform_factory(translation_model,
                    exclude=[info['translation_model_fk']], formfield_callback=formfield_callback)
                new_class.declared_fields.update(new_class.child_form_class.declared_fields)
                new_class.base_fields.update(new_class.child_form_class.base_fields)
        return new_class
        
class TranslationModelForm(ModelForm):
    __metaclass__ = TranslationModelFormMetaclass
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
        initial={}, error_class=ErrorList, label_suffix=':',
        empty_permitted=False, instance=None):
        
        model = self._meta.model
        child_model = self.child_form_class._meta.model
        translation_info = translation_pool.get_info(model)
        current_language = self.base_fields['language'].initial
        if instance and instance.pk:
            try:
                child_instance = child_model.objects.get(**{
                    translation_info['translation_model_fk']: instance.pk,
                    translation_info['language_field']: current_language})
            except child_model.DoesNotExist:
                child_instance = child_model(**{
                    translation_info['language_field']: current_language})
        else:
            child_instance = child_model(**{translation_info['language_field']: current_language})
            
        initial.update(model_to_dict(child_instance))
        self.child_form = self.child_form_class(data=data, files=files, auto_id=auto_id, prefix=prefix,
            initial=initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=child_instance)
            
        
        super(TranslationModelForm, self).__init__(data=data, files=files, auto_id=auto_id, prefix=prefix,
            initial=initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=instance)
    __init__.testvar = True

    def full_clean(self):
        super(TranslationModelForm, self).full_clean()
        self.child_form.full_clean()
        if self.child_form._errors:
            self._update_errors(self.child_form._errors)
            del self.cleaned_data
    
def translation_modelform_factory(model, form=TranslationModelForm, fields=None, exclude=None,
    formfield_callback=None):
    # Create the inner Meta class. FIXME: ideally, we should be able to
    # construct a ModelForm without creating and passing in a temporary
    # inner class.
    translation_info = translation_pool.get_info(model)
    translation_model = translation_info['model']
    translation_fields = [f[0].name for f in translation_model._meta.get_fields_with_model()]
    # Build up a list of attributes that the Meta object will have.
    attrs = {'model': model}
    if fields is not None:
        attrs['fields'] = [ field for field in fields if not field in translation_fields]
    if exclude is not None:
        attrs['exclude'] = exclude

    # If parent form class already has an inner Meta, the Meta we're
    # creating needs to inherit from the parent's inner meta.
    parent = (object,)
    if hasattr(form, 'Meta'):
        parent = (form.Meta, object)
    Meta = type('Meta', parent, attrs)

    # Give this new form class a reasonable name.
    class_name = model.__name__ + 'Form'

    # Class attributes for the new form class.
    form_class_attrs = {
        'Meta': Meta,
        'formfield_callback': formfield_callback
    }

    return TranslationModelFormMetaclass(class_name, (form,), form_class_attrs)