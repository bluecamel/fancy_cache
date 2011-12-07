from django.shortcuts import get_object_or_404
from functools import partial

def get_object_or_404_cache_verbose(request, model, *args, **kwargs):
    instance, cache_info = request.fancy_cache.get_or_set(
        partial(get_object_or_404, model, *args, **kwargs),
        model.__name__, # use model name for fragment name
        [ # vary on
            '-'.join([str(arg) for arg in args]), # list of positional args
            '-'.join(kwargs.keys()), # list of field lookups
            '-'.join(str(value) for value in kwargs.values()) # list of values
        ],
        verbose=True
    )
    return (instance, cache_info)

def get_object_or_404_cache(request, model, *args, **kwargs):
    instance, cache_info = get_object_or_404_cache_verbose(request, model, *args, **kwargs)
    return instance