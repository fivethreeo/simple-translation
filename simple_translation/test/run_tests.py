import sys

def run_tests():
    
    from django.conf import settings
    
    settings.configure(
        DATABASES = {
            'default':  {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'simple_translation.db'
            }
        },
        
        TEMPLATE_CONTEXT_PROCESSORS = (
            "django.core.context_processors.auth",
            "django.core.context_processors.i18n",
            "django.core.context_processors.debug",
            "django.core.context_processors.request",
            "django.core.context_processors.media",
            'django.core.context_processors.csrf',
        ),
        
        
        MIDDLEWARE_CLASSES = [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.doc.XViewMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
        ],
        
        ROOT_URLCONF = 'simple_translation.test.testapp.no_translated_urls',
        
        INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.admin',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'simple_translation',
            'simple_translation.test.testapp'
        ),
        
        LANGUAGE_CODE = "en",
        
        LANGUAGES = (
            ("en", "English"),
            ("de", "German"),
        ),
        
        SITE_ID = 1
        

    )
    
    from django.test.utils import get_runner

    failures = get_runner(settings)().run_tests(['simple_translation'])
    sys.exit(failures)

if __name__ == '__main__':
    run_tests()