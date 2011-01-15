from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('')
for langcode in dict(settings.LANGUAGES).keys():
	urlpatterns += url(r'^%s/' % langcode,
		include('simple_translation.test.testapp.urls',
		namespace=langcode, app_name='testapp')
	)