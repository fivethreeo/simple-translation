from simple_translation.test.testapp.models import Entry, EntryTitle
from simple_translation.translation_pool import translation_pool

translation_pool.register_translation(Entry, EntryTitle)

