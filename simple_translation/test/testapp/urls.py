from simple_translation.test.testapp.models import EntryTitle
from django.conf.urls.defaults import *

entry_info_dict = {
    'queryset': EntryTitle.objects.all(),
    'date_field': 'pub_date',
    'allow_future': True
}

entry_info_tagged_dict = {
    'queryset_or_model': EntryTitle.objects.all(),
}

entry_info_month_dict = {
    'queryset': EntryTitle.objects.all(),
    'date_field': 'pub_date',
    'month_format': '%m',
}

entry_info_detail_dict = dict(entry_info_month_dict, slug_field='entrytitle__slug')

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.date_based.archive_index', entry_info_dict, 'entry_archive_index'),
    
    (r'^(?P<year>\d{4})/$', 
        'django.views.generic.date_based.archive_year', entry_info_dict, 'entry_archive_year'),
    
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/$', 
        'django.views.generic.date_based.archive_month', entry_info_month_dict, 'entry_archive_month'),
    
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 
        'django.views.generic.date_based.archive_day', entry_info_month_dict, 'entry_archive_day'),
    
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 
        'django.views.generic.date_based.object_detail', entry_info_detail_dict, 'entry_detail')
    
)