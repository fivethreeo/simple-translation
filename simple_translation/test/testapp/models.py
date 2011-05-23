import datetime

from django.db import models
from django.conf import settings

class Entry(models.Model):
    is_published = models.BooleanField()

class EntryTitle(models.Model):
    entry = models.ForeignKey(Entry)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    pub_date = models.DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.title
        
    def _get_absolute_url(self):
        language_namespace = 'simple_translation.middleware.MultilingualGenericsMiddleware' in settings.MIDDLEWARE_CLASSES and '%s:' % self.language or ''
        return ('%sentry_detail' % language_namespace, (), {
            'year': self.pub_date.strftime('%Y'),
            'month': self.pub_date.strftime('%m'),
            'day': self.pub_date.strftime('%d'),
            'slug': self.slug
        })
    get_absolute_url = models.permalink(_get_absolute_url)