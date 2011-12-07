from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('fancy_cache.views',
    url(r'^$', 'home', name='fancy_cache_home'),
    url(r'^key/$', 'key_list', name='fancy_cache_key_list'),
    #url(r'^key/delete/(?P<key>[-_|%\w\d\.\/\'\"]+)/$', 'key_delete', name='fancy_cache_key_delete'),
    url(r'^stats/$', 'stats_list', name='fancy_cache_stats_list'),
)