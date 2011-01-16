from simple_translation.test.testcases import SimpleTranslationBaseTestCase
from django.core.urlresolvers import reverse
from django.conf import settings

class SimpleTranslationTestCase(SimpleTranslationBaseTestCase):
    
    def test_01_test_translated_urls(self):
        
        old_urlconf  = settings.ROOT_URLCONF
        settings.ROOT_URLCONF = 'simple_translation.test.testapp.translated_urls'
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'simple_translation.middleware.MultilingualGenericsMiddleware']

        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        
        de_title = create_entry_title(entry, language='de')
                
        index = reverse('entry_index')
        
        en_index = reverse('en:entry_index')
        de_index = reverse('de:entry_index')
        
        self.assertEquals(en_index, '')        
        self.assertEquals(de_index, '')
        
        response = self.client.get(index)
        self.assertContains(response.content, 'english')
        self.assertContains(response.content, 'german')

        response = self.client.get(en_index)
        self.assertContains(response.content, 'english')
        
        response = self.client.get(de_index)
        self.assertContains(response.content, 'german')
        
        settings.ROOT_URLCONF = old_urlconf
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_02_test_no_translated_urls_with_middleware(self):
        
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'simple_translation.middleware.MultilingualGenericsMiddleware']
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        
        de_title = create_entry_title(entry, language='de')        	
        index = reverse('entry_index')
        
        response = self.client.get(index)
        self.assertContains(response.content, 'english')
        self.assertContains(response.content, 'german')
        
        settings.MIDDLEWARE_CLASSES = old_middleware
        
    def test_03_test_no_translated_urls_without_middleware(self):
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        
        de_title = create_entry_title(entry, language='de')        	
        index = reverse('entry_index')
        
        response = self.client.get(index)
        self.assertContains(response.content, 'english')
        self.assertContains(response.content, 'german')

    def test_04_test_no_translated_urls_with_locale_middleware(self):
        
        old_middleware = settings.MIDDLEWARE_CLASSES
        settings.MIDDLEWARE_CLASSES = old_middleware +[
            'django.middleware.locale.LocaleMiddleware']
            
        published_at = datetime.datetime.now() - datetime.timedelta(hours=-1)
        en_title, entry = self.create_entry_with_title(published=True, 
            published_at=published_at)
        
        de_title = create_entry_title(entry, language='de')
        
        index = reverse('entry_index')
        
        response = self.client.get(index)
        self.assertContains(response.content, 'english')
        self.assertContains(response.content, 'german')
        
        settings.MIDDLEWARE_CLASSES = old_middleware
        