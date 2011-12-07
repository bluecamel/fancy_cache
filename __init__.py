import datetime
import urllib

from django.core.cache import cache
from django.utils.http import urlquote
from django.utils.hashcompat import md5_constructor

from django.shortcuts import get_object_or_404
from functools import partial

from fancy_cache.memcached_stats import MemcachedStats

class FancyCache(object):
    _view_keys = None
    _template_keys = None

    def __init__(self):
        self._view_keys = []
        self._template_keys = []

    def get_keys(self):
        return {'view_keys': self._view_keys, 'template_keys': self._template_keys}

    def get_memcached_clients(self):
        clients = []
        for server in cache._cache.servers:
            clients.append(
                MemcachedStats(server.ip, server.port)
            )
        return clients

    def get_object_or_404(self, model, *args, **kwargs):
        from django.shortcuts import get_object_or_404

        expire_time = kwargs.pop('expire_time', 0)

        vary_on = [model.__name__]
        vary_on.extend(args)
        for key, value in kwargs.items():
            vary_on.append('{key}={value}'.format(key=key, value=value))

        obj = self.get_or_set(
            partial(get_object_or_404, model, *args, **kwargs),
            'get_object_or_404',
            vary_on,
            expire_time=expire_time
        )

        pk = obj.pk

        return obj

    def get_or_set(self, default, fragment_name, vary_on_a=None, vary_on_b=None, expire_time=0, template=False, verbose=False):
        from django.conf import settings

        vary_on = []

        for vary in (vary_on_a, vary_on_b):
            if vary:
                if isinstance(vary, dict):
                    vary_on.extend(
                        ('='.join((str(key), str(value))) for key, value in vary.items())
                    )
                else:
                    try:
                        vary_on.extend(
                            (str(value) for value in vary)
                        )
                    except TypeError:
                        raise AttributeError('vary_on_a and vary_on_b, if specified, must be a dict or an iterable.')

        if fragment_name == settings.FANCY_CACHE_MANAGER_CACHE_KEY:
            args_str = u''
            key = settings.FANCY_CACHE_MANAGER_CACHE_KEY
        else:
            args_str = u':'.join(str(var) for var in vary_on)
            args = urlquote(args_str)
            args_hash = md5_constructor(args).hexdigest()
            key = 'cache.{fragment_name}.{args}'.format(fragment_name=fragment_name, args=args_hash)

        value = cache.get(key)
        if value is None:
            if callable(default):
                value = default()
            else:
                value = default

            cache.set(key, value, expire_time)

        if expire_time == 0:
            expire_time = 'indefinite'
        else:
            expire_time = datetime.datetime.now() + datetime.timedelta(seconds=expire_time)

        if template:
            self._template_keys.append((key, fragment_name, args_str, expire_time))
        else:
            self._view_keys.append((key, fragment_name, args_str, expire_time))

        if verbose:
            return (value, {'key': key, 'vary_args': args_str})
        else:
            return value

    def key_list_reset(self):
        from django.conf import settings

        #cache.delete(settings.FANCY_CACHE_MANAGER_CACHE_KEY)

        for client in self.get_memcached_clients():
            stats = client.stats()

            # This is stupid, but currently is the only way I can clear the slabs.
            for key, size, time_stamp in client.key_details():
                value = cache.get(key)

def inject_app_defaults(application):
    """
    Borrowed from: https://github.com/thsutton/django-application-settings/

    Inject an application's default settings
    """

    try:
        __import__('{application}.settings'.format(application=application))
        import sys

        # Import our defaults, project defaults, and project settings
        _app_settings = sys.modules['{application}.settings'.format(application=application)]
        _def_settings = sys.modules['django.conf.global_settings']
        _settings = sys.modules['django.conf'].settings

        # Add the values from the application.settings module
        for _k in dir(_app_settings):
            if _k.isupper():
                # Add the value to the default settings module
                setattr(_def_settings, _k, getattr(_app_settings, _k))

                # Add the value to the settings, if not already present
                if not hasattr(_settings, _k):
                    setattr(_settings, _k, getattr(_app_settings, _k))

    except ImportError:
        # Silently skip failing settings modules
        pass

inject_app_defaults(__name__)
