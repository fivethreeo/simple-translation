from django.template.defaultfilters import slugify
from django.test.testcases import TestCase
from simple_trasnslation.test.models import Entry, EntryTitle

class SimpleTranslationBaseTestCase(TestCase):
        
    def create_entry_with_title(self, title=None, slug=None, language=None, published_at=None):
        if published_at:
            kwargs['pub_date'] = published_at
        entry = Entry.objects.create(**kwargs)
        entrytitle = self.create_entry_title(entry, title=title, slug=slug, language=language)
        return (entrytitle, entry)
        
    def create_entry_title(self, entry, title=None, slug=None, language=None):
        if not title:
            title = 'Entry title'
        slug = slug or slugify(title)
        language = language or 'en'
        return entry.entrytitle_set.create(entry=entry, title=title, slug=slug, language=language)