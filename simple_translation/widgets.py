from django.conf import settings

from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django import forms

from simple_translation.translation_pool import translation_pool

class LanguageWidget(forms.HiddenInput):
    
    def __init__(self, *args, **kwargs):
        self.translation = kwargs.pop('translation')
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
        
        buttons = []
        for lang in settings.LANGUAGES:
            button_classes = u'class="language_button%s"' % (lang[0] == value and ' selected' or '')
            buttons.append(u''' <input onclick="trigger_lang_button(this,'./?language=%s');"%s id="debutton" name="%s" value="%s" type="button">''' % (
                lang[0], button_classes, lang[0], lang[1]))
                
        lang_descr = _('Delete: &quot;%s&quot; translation.') % force_unicode(lang_dict[str(value)]) 
        if self.translation.pk and len(translation_pool.annotate_with_translations(self.translation).translations) > 1:
            buttons.append(u'''&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input onclick="trigger_lang_button(this,'delete-translation/?language=%s');"%s id="debutton" name="%s" value="%s" type="button">''' % (
                    value, u'', 'dellang', lang_descr ))    
                
        tabs = u"""%s%s<div id="page_form_lang_tabs">%s</div>""" % (self.button_js, hidden_input, u''.join(buttons))

        return mark_safe(tabs)
