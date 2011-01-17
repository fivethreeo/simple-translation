import datetime
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User

from simple_translation.test.testcases import SimpleTranslationBaseTestCase

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
        
        # edit english
        response = self.client.get(edit_url, {'language': 'en'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'language_button selected" id="debutton" name="en"' )
        
        # edit german
        response = self.client.get(edit_url, {'language': 'de'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'language_button selected" id="debutton" name="de"' )
        
        
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
