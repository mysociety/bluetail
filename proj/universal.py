from django.conf import settings # import the settings file

def universal_context(request):
    """
    returns helpful universal context to the views
    """

    
    return {'IS_LIVE': settings.IS_LIVE,
            'settings':settings,
            'request':request,
            'current_path': settings.SITE_ROOT + request.get_full_path(),
            'SITE_ROOT':settings.SITE_ROOT}