from django.conf import settings

from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django import forms

from simple_translation.translation_pool import translation_pool

class LanguageWidget(forms.HiddenInput):
	
    class Media:
    	# use getattr until django-cms reccomends django 1.3
    	css = {
    		'all': ['%ssimple_translation/widget.css' % getattr(settings, 'STATIC_URL', '')]
    	}
    	js = ['%ssimple_translation/widget.js' % getattr(settings, 'STATIC_URL', '')]
    	
    def __init__(self, *args, **kwargs):
        self.translation_of_obj = kwargs.pop('translation_of_obj')
        self.translation_obj = kwargs.pop('translation_obj')
        self.static = 'django.contrib.staticfiles' in settings.INSTALLED_APPS
        
        super(LanguageWidget, self).__init__(*args, **kwargs)
            
    is_hidden = False
    button_js = u'''
    <script type="text/javascript">
    
    var changed = false
    
    django.jQuery(document).ready(function () {
        django.jQuery("#id_slug").change(function() { changed = true; });
        django.jQuery('#id_title').change(function() { changed = true; });
    })  
    
    trigger_lang_button = function(e, url) {
        // also make sure that we will display the confirm dialog
        // in case users switch tabs while editing plugins
        
        if(django.jQuery("iframe").length){
            changed = true;
        }

        if (changed) {
            var question = gettext("Are you sure you want to change tabs without saving the page first?")
            var answer = confirm(question);
        }else{
            var answer = true;
        }

        if (!answer) {
            return false;
        } else {
            window.location = url;
        }
    }
  
    </script>
    '''
    
    def render(self, name, value, attrs=None):
        
        hidden_input = super(LanguageWidget, self).render(name, value, attrs=attrs)
        lang_dict = dict(settings.LANGUAGES)
        
        current_languages = []
        translation_of_obj = self.translation_of_obj
        if translation_of_obj and translation_of_obj.pk:
            info = translation_pool.get_info(translation_of_obj.__class__)
            translation_of_obj = translation_pool.annotate_with_translations(translation_of_obj)
            for translation in translation_of_obj.translations:
                current_languages.append(getattr(translation, info.language_field))
                
        buttons = []
        for lang in settings.LANGUAGES:
            current_lang = lang[0] == value
            language_exists = lang[0] in current_languages
            button_classes = u'class="%s"' % (
                (not self.static and 'button') or current_lang and 'simple-translation-current' or language_exists and 'simple-translation-exists' or '',
            )
            disabled = current_lang and 'disabled' or ''
            buttons.append(u''' <input onclick="trigger_lang_button(this,'./?language=%s');"
                %s name="%s" value="%s" type="button" %s>''' % (
                    lang[0], button_classes, lang[0], lang[1], disabled
                )
            )
                     
        if self.translation_obj.pk and len(current_languages) > 1:
            lang_descr = _('Delete: &quot;%s&quot; translation.') % force_unicode(lang_dict[str(value)])
            buttons.append(u'''&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <input onclick="trigger_lang_button(this,'delete-translation/?language=%s');"
            %s name="%s" value="%s" type="button">''' % (
                value, u'class="%s"' % (not self.static and 'button default' or 'simple-translation-delete'), 'language_delete', lang_descr
                )
            )    
                    
        tabs = u"""%s%s%s""" % (self.button_js, hidden_input, u''.join(buttons))

        return mark_safe(tabs)
