from django.conf import settings

def get_language_from_request(request):
    return request.REQUEST.get('language', getattr(request, 'LANGUAGE_CODE', settings.LANGUAGE_CODE))
