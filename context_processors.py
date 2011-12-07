from django.conf import settings

def base_content(request):
    """
    Use this to expose variables to the template Context.
    """
    data = {}
    data.update({'FANCY_CACHE_MEDIA_URL': settings.FANCY_CACHE_MEDIA_URL})
    data.update({'DAJAXICE_JS_URL': settings.DAJAXICE_JS_URL})
    data.update({'JQUERY_JS_URL': settings.JQUERY_JS_URL})
    data.update({'JQUERY_TABLESORTER_JS_URL': settings.JQUERY_TABLESORTER_JS_URL})
    data.update({'JQUERY_UITABLEFILTER_JS_URL': settings.JQUERY_UITABLEFILTER_JS_URL})

    if not request.is_crawler:
        if request.user.has_perm('fancy_cache.view_manager'):
            data.update({'perm_view_manager': True})
        if request.user.has_perm('fancy_cache.key_delete'):
            data.update({'perm_key_delete': True})
    return data