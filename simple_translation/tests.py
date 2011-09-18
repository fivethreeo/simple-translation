import datetime
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.template import Template, Context
from simple_translation.test.testcases import SimpleTranslationBaseTestCase
from simple_translation.translation_pool import TranslationPool

class SimpleTranslationTestCase(SimpleTranslationBaseTestCase):

    def test_01_test_translated_urls(self):
        
        old_urlconf  = settings.ROOT_URLCONF
        settings.ROOT_URLCONF = 'simple_translation.test.testapp.translated_urls'
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'simple_translation.middleware.MultilingualGenericsMiddleware']

        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
            
        index = reverse('entry_archive_index')
        
        en_index = reverse('en:entry_archive_index')
        de_index = reverse('de:entry_archive_index')
        
        self.assertEquals(index, '/')        
        self.assertEquals(en_index, '/en/')        
        self.assertEquals(de_index, '/de/')
        
        response = self.client.get(index)
        self.assertContains(response, 'english')

        response = self.client.get(en_index)
        self.assertContains(response, 'english')
        self.assertNotContains(response, 'german')

        response = self.client.get(de_index)
        self.assertContains(response, 'german')
        self.assertNotContains(response, 'english')
        
        settings.ROOT_URLCONF = old_urlconf
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_02_test_no_translated_urls_with_middleware(self):
        
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'simple_translation.middleware.MultilingualGenericsMiddleware']
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
            	
        index = reverse('entry_archive_index')
        
        response = self.client.get(index)
        self.assertContains(response, 'english')
        
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_03_test_no_translated_urls_without_middleware(self):
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
                	
        index = reverse('entry_archive_index')
        
        response = self.client.get(index)
        self.assertContains(response, 'english')
        self.assertContains(response, 'german')

    def test_04_test_no_translated_urls_with_locale_middleware(self):
        
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware + [
            'django.middleware.locale.LocaleMiddleware',
            'simple_translation.middleware.MultilingualGenericsMiddleware']
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
        
        index = reverse('entry_archive_index')
        
        response = self.client.get(index)
        self.assertContains(response, 'english')
        self.assertNotContains(response, 'german')
        
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_05_test_translated_urls_with_locale_middleware(self):
        
        old_urlconf  = settings.ROOT_URLCONF
        settings.ROOT_URLCONF = 'simple_translation.test.testapp.translated_urls'
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'django.middleware.locale.LocaleMiddleware',
            'simple_translation.middleware.MultilingualGenericsMiddleware']
        
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
            
        index = reverse('entry_archive_index')
        
        en_index = reverse('en:entry_archive_index')
        de_index = reverse('de:entry_archive_index')
        
        self.assertEquals(index, '/')        
        self.assertEquals(en_index, '/en/')        
        self.assertEquals(de_index, '/de/')
        
        response = self.client.get(index)
        self.assertContains(response, 'english') # localemiddleware wins
        self.assertNotContains(response, 'german')

        response = self.client.get(en_index)
        self.assertContains(response, 'english')
        self.assertNotContains(response, 'german')

        response = self.client.get(de_index)
        self.assertContains(response, 'german')
        self.assertNotContains(response, 'english') # generics middleware wins
        
        settings.ROOT_URLCONF = old_urlconf
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_06_admin_edit_translated_entry(self):
        
        superuser = User(username="super", is_staff=True, is_active=True, 
            is_superuser=True)
        superuser.set_password("super")
        superuser.save()
        
        self.client.login(username='super', password='super')
        
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
        
        edit_url = reverse('admin:testapp_entry_change', args=(str(entry.pk)))
        
        # edit english(default)
        response = self.client.get(edit_url)

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'simple-translation-current" name="en"' )
        
        # edit english
        response = self.client.get(edit_url, {'language': 'en'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'simple-translation-current" name="en"' )
        
        # edit german
        response = self.client.get(edit_url, {'language': 'de'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'simple-translation-current" name="de"' )
        
        
    def test_07_test_changelist_description(self):
        superuser = User(username="super", is_staff=True, is_active=True, 
            is_superuser=True)
        superuser.set_password("super")
        superuser.save()
        
        self.client.login(username='super', password='super')
        
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
            
        list_url = reverse('admin:testapp_entry_changelist')
        response = self.client.get(list_url)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '<a href="1/?language=en">EN</a>' )
        self.assertContains(response, '<a href="1/?language=de">DE</a>' )
        
    def test_08_test_filters(self):
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
        
        class MockRequest(object):
            LANGUAGE_CODE  = 'en'
            REQUEST = {}
            
        request = MockRequest()
        
        ctxt = Context({'entry': entry, 'request': request})
        
        tpl_req = Template('''{% load simple_translation_tags %}
            {% with entry|get_preferred_translation_from_request:request as title %}
                {{ title }}
            {% endwith %}
        ''')
        
        self.assertEquals(tpl_req.render(ctxt).strip(), 'english')
        
        tpl_lang = Template('''{% load simple_translation_tags %}
            {% with entry|get_preferred_translation_from_lang:'de' as title %}
                {{ title }}
            {% endwith %}
        ''')
        self.assertEquals(tpl_lang.render(ctxt).strip(), 'german')
        
    def test_09_test_respect_settings_languages(self):
        settings.LANGUAGES = (
            ('en', 'English'),
            ('pl', 'Polish'),
        )
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
        pl_title = self.create_entry_title(entry, title='polish', language='pl', published_at=published_at)

        pool = TranslationPool()
        
        pool.annotate_with_translations(entry)
        translated_languages = [t.language for t in entry.translations]
        self.assertIn('pl', translated_languages)
        self.assertIn('en', translated_languages)
        self.assertNotIn('de', translated_languages)

    def test_10_test_respect_settings_languages_order(self):
        settings.LANGUAGES = (
            ('pl', 'Polish'),
            ('en', 'English'),
            ('de', 'German')
        )
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(title='english', published_at=published_at)
        de_title = self.create_entry_title(entry, title='german', language='de', published_at=published_at)
        pl_title = self.create_entry_title(entry, title='polish', language='pl', published_at=published_at)

        pool = TranslationPool()
        
        pool.annotate_with_translations(entry)
        translated_languages = [t.language for t in entry.translations]
        settings_languages = [lang_code for lang_code, language in settings.LANGUAGES]
        self.assertSequenceEqual(translated_languages, settings_languages)

    def test_11_test_respect_settings_languages_list(self):
        settings.LANGUAGES = (
            ('en', 'English'),
            ('pl', 'Polish'),
        )
        entries = []
        for title in ('title1', 'title2'):
            published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
            en_title, entry = self.create_entry_with_title(title='english' + title, published_at=published_at)
            de_title = self.create_entry_title(entry, title='german' + title, language='de', published_at=published_at)
            pl_title = self.create_entry_title(entry, title='polish' + title, language='pl', published_at=published_at)
            entries.append(entry)

        pool = TranslationPool()
        
        pool.annotate_with_translations(entries)
        for entry in entries:
            translated_languages = [t.language for t in entry.translations]
            self.assertIn('pl', translated_languages)
            self.assertIn('en', translated_languages)
            self.assertNotIn('de', translated_languages)

    def test_12_test_respect_settings_languages_order_list(self):
        settings.LANGUAGES = (
            ('pl', 'Polish'),
            ('en', 'English'),
            ('de', 'German')
        )
        entries = []
        for title in ('title1', 'title2'):
            published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
            en_title, entry = self.create_entry_with_title(title='english'+title, published_at=published_at)
            de_title = self.create_entry_title(entry, title='german'+title, language='de', published_at=published_at)
            pl_title = self.create_entry_title(entry, title='polish'+title, language='pl', published_at=published_at)
            entries.append(entry)
            
        pool = TranslationPool()
        
        pool.annotate_with_translations(entries)
        
        settings_languages = [lang_code for lang_code, language in settings.LANGUAGES]
        for entry in entries:
            translated_languages = [t.language for t in entry.translations]
            self.assertSequenceEqual(translated_languages, settings_languages)
