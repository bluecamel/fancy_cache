from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def flush(request):
    """
    Flush the cache.
    """
    data = {'success': False}

    if request.user.has_perm('fancy_cache.key_delete'):
        cache.clear()
        data['success'] = True
    else:
        data['message'] = 'You do not have permission to delete cached items.'

    return simplejson.dumps(data)

@dajaxice_register
def key_delete(request, key=None):
    """
    Delete the given key.
    """
    data = {'success': False}

    if request.user.has_perm('fancy_cache.key_delete'):
        if key:
            cache.delete(key)
            cache.delete(settings.FANCY_CACHE_MANAGER_CACHE_KEY)
            data['success'] = True
    else:
        data['message'] = 'You do not have permission to delete cached items.'

    return simplejson.dumps(data)

@dajaxice_register
def key_list_reset(request):
    """
    Clear the cached list of keys.
    Clear the slabs.
    """
    data = {'success': False}

    if request.user.has_perm('fancy_cache.key_delete'):
        request.fancy_cache.key_list_reset()
        data['success'] = True
    else:
        data['message'] = 'You do not have permission to delete cached items.'

    return simplejson.dumps(data)

@dajaxice_register
def multi_key_delete(request, keys=None):
    """
    Delete the given keys.
    """
    data = {'success': False}

    if request.user.has_perm('fancy_cache.key_delete'):
        cache.delete_many(keys)
        cache.delete(settings.FANCY_CACHE_MANAGER_CACHE_KEY)
        data['success'] = True
    else:
        data['message'] = 'You do not have permission to delete cached items.'

    return simplejson.dumps(data)
