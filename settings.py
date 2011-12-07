from django.conf import settings

if not hasattr(settings, 'FANCY_CACHE_SHOW_PANEL'):
    settings.FANCY_CACHE_SHOW_PANEL = True

if not hasattr(settings, 'FANCY_CACHE_SHOW_PANEL_IN_ADMIN'):
    settings.FANCY_CACHE_SHOW_PANEL_IN_ADMIN = False

if not hasattr(settings, 'FANCY_CACHE_MEDIA_URL'):
    media_url = getattr(settings, 'MEDIA_URL', '/static/')
    settings.FANCY_CACHE_MEDIA_URL = '{media_url}fancy_cache/'.format(media_url=media_url)

if not hasattr(settings, 'DAJAXICE_JS_URL'):
    settings.DAJAXICE_JS_URL = None

if not hasattr(settings, 'JQUERY_JS_URL'):
    settings.JQUERY_JS_URL = '{fc_media_url}js/jquery-1.6.2.min.js'.format(fc_media_url=settings.FANCY_CACHE_MEDIA_URL)

if not hasattr(settings, 'JQUERY_TABLESORTER_JS_URL'):
    settings.JQUERY_TABLESORTER_JS_URL = '{fc_media_url}js/jquery.tablesorter.min.js'.format(fc_media_url=settings.FANCY_CACHE_MEDIA_URL)

if not hasattr(settings, 'JQUERY_UITABLEFILTER_JS_URL'):
    settings.JQUERY_UITABLEFILTER_JS_URL = '{fc_media_url}js/jquery.uitablefilter.js'.format(fc_media_url=settings.FANCY_CACHE_MEDIA_URL)

if not hasattr(settings, 'FANCY_CACHE_MANAGER_CACHE_TIME'):
    settings.FANCY_CACHE_MANAGER_CACHE_TIME = 300

if not hasattr(settings, 'FANCY_CACHE_MANAGER_CACHE_KEY'):
    settings.FANCY_CACHE_MANAGER_CACHE_KEY = 'get_memcached_clients'