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

    2. simple-translation has one dependency - ``django-cms``. If ``cms`` is not
       in your `INSTALLED_APPS` list, add it.

    3. For the models to be translatable, create a ``cms_translation.py`` file 
       where you register the translated model in the translation_pool. ::
       
            from django.contrib import admin
            from models import Entry, EntryTitle
            
            from simple_translation.translation_pool import translation_pool
            translation_pool.register(Entry, EntryTitle)
      
    4. To be able to edit the translated models in the admin.
       Register the models using the custom ``TranslationAdmin`` ``ModelAdmin``. ::
       
            from django.contrib import admin
            from models import Entry, EntryTitle
            from simple_translation.admin import TranslationAdmin
            
            class EntryAdmin(TranslationAdmin):
                pass
            
            admin.site.register(Entry, EntryAdmin)
            
    .. admonition:: Note
        
        Make sure ``'languages'`` is listed in ``list_display``.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

