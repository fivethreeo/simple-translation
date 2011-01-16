from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
)

urlpatterns +=  patterns('', url(r'^',
    include('simple_translation.test.testapp.urls', app_name='testapp')
    )
)

for langcode in dict(settings.LANGUAGES).keys():
    urlpatterns +=  patterns('', url(r'^%s/' % langcode,
        include('simple_translation.test.testapp.urls',
            namespace=langcode, app_name='testapp'),
        kwargs={'language_code': langcode}
    )
)

