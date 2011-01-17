from django import forms
from django.contrib import admin
from simple_translation.admin import TranslationAdmin

from simple_translation.test.testapp.models import Entry, EntryTitle
from simple_translation.admin import TranslationModelForm

class EntryForm(TranslationModelForm):
    
    class Meta:
        model = Entry
    
class EntryAdmin(TranslationAdmin):
    
    form = EntryForm
    
    prepopulated_fields = {}
        
    list_display = ('description', 'languages', 'is_published')
    list_editable = ('is_published',)
    
    def __init__(self, *args, **kwargs):
        super(EntryAdmin, self).__init__(*args, **kwargs)
        self.prepopulated_fields.update({'slug': ('title',)})
        
    def get_fieldsets(self, request, obj=None):
        fieldsets = super(EntryAdmin, self).get_fieldsets(request, obj=obj)
        fieldsets[0] = (None, {'fields': (
            'language',
            'pub_date',
            'title',
            'slug'
        )})
        return fieldsets
           
admin.site.register(Entry, EntryAdmin)