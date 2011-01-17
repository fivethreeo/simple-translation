.. simple-translation documentation master file, created by
   sphinx-quickstart on Tue Aug 31 16:36:25 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================
simple-translation
=====================

.. module:: simple_translation
   :synopsis: Simple translation

Overview
========

There are four steps for using simple-translation:

    1. Make two models in your app, one having the non-translated fields and
       the other having the translated fields a language field and
       a ForeignKey to the non-translated model. ::
       
            from django.db import models
            from cms import settings
            
            class Entry(models.Model):
                published = models.BooleanField()
            
            class EntryTitle(models.Model):
                entry = models.ForeignKey(Entry)
                language = models.CharField(max_length=2, choices=settings.LANGUAGES)
                title = models.CharField(max_length=255)

    2. For the models to be translatable, create a ``simple_translate.py`` file 
       where you register the translated model in the translation_pool. ::
       
            from models import Entry, EntryTitle
            
            from simple_translation.translation_pool import translation_pool
            translation_pool.register(Entry, EntryTitle)
      
    3. To be able to edit the translated models in the admin.
       Register the models using the custom ``TranslationAdmin`` ``ModelAdmin``. ::
       
            from django.contrib import admin
            from models import Entry
            from simple_translation.admin import TranslationAdmin
            
            class EntryAdmin(TranslationAdmin):
                pass
            
            admin.site.register(Entry, EntryAdmin)
            
        .. admonition:: Note
        
            Make sure ``'languages'`` is listed in ``list_display``.
    
    4. To use the generics views middleware with namespaced urls:
    
        Add ``'simple_translation.middleware import MultilingualGenericsMiddleware'`` to ``settings.MIDDLEWARE_CLASSES``
        
        Set up some urls using generic views: ::
        
            # urls.py
            from models import Entry
            from django.conf.urls.defaults import *
            
            entry_info_dict = {
                'queryset': Entry.objects.all(),
                'date_field': 'pub_date',
                'allow_future': True,
                'slug_field': 'entrytitle__slug'
            }
            
            urlpatterns = patterns('',
                
                (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 
                    'django.views.generic.date_based.object_detail', entry_info_dict, 'entry_detail')
                
            )
            
        Wrap the urls to namespace them: ::
        
            # translated_urls.py
            from django.conf import settings
            from django.conf.urls.defaults import *
                        
            urlpatterns +=  patterns('', url(r'^',
                include('appname.urls', app_name='appname')
                )
            )
            
            for langcode in dict(settings.LANGUAGES).keys():
                urlpatterns +=  patterns('', url(r'^%s/' % langcode,
                    include('appname.urls',
                        namespace=langcode, app_name='appname'),
                    kwargs={'language_code': langcode}
                )
            )
        
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

