import datetime

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from operator import itemgetter

@staff_member_required
def home(request):
    context = {}
    context['page_title'] = 'Home'
    return render_to_response('fancy_cache/base.html', context, context_instance=RequestContext(request))

@staff_member_required
def key_list(request):
    context = {}
    context['page_title'] = 'List Keys'

    def get_memcached_clients():
        memcached_clients = request.fancy_cache.get_memcached_clients()

        servers = []

        for client in memcached_clients:
            stats = client.stats()

            keys = []

            for key, size, time_stamp in client.key_details():
                size = size.rstrip(' b')
                time_stamp = time_stamp.rstrip(' s')

                elapsed_time = int(stats['time']) - int(stats['uptime'])
                if time_stamp == elapsed_time:
                    seconds_remaining = 100000
                    expire_time = 'Infinite'
                elif time_stamp > elapsed_time:
                    seconds_remaining = int(time_stamp) - int(elapsed_time)
                    expire_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds_remaining)
                else:
                    seconds_remaining = 0
                    expire_time = '?'

                keys.append({
                    'key': key,
                    'size': size,
                    'seconds_remaining': seconds_remaining,
                    'expire_time': expire_time
                })

            keys = sorted(keys, key=itemgetter('key'))

            servers.append({
                'host': client._host,
                'port': client._port,
                'keys': keys
            })

        return servers

    #context['servers'] = request.fancy_cache.get_or_set(
    #    get_memcached_clients,
    #    settings.FANCY_CACHE_MANAGER_CACHE_KEY,
    #    expire_time=settings.FANCY_CACHE_MANAGER_CACHE_TIME
    #)
    context['servers'] = get_memcached_clients()

    return render_to_response('fancy_cache/key_list.html', context, context_instance=RequestContext(request))

@staff_member_required
def stats_list(request):
    context = {}
    context['page_title'] = 'Server Stats'

    servers = []

    for client in request.fancy_cache.get_memcached_clients():
        stats = client.stats()
        servers.append({
            'host': client._host,
            'port': client._port,
            'stats': [{
                'name': name,
                'value': stats[name]
            } for name in sorted(stats)]
        })

    context['servers'] = servers

    return render_to_response('fancy_cache/stats_list.html', context, context_instance=RequestContext(request))