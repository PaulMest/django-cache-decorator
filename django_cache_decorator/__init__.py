# -*- coding: utf-8 -*- 
from __future__ import absolute_import
from __future__ import unicode_literals

'''
Forked from https://github.com/rchrd2/django-cache-decorator

This can be used to cache the results of functions.

Example:
  @django_cache_decorator(time=0)
  def geocodeGooglePlaceTextJson(location):
      ...

Built off of code form:
http://james.lin.net.nz/2011/09/08/python-decorator-caching-your-functions/
'''
from django_cache_decorator.utils import cache_get_key

# New cache instance reconnect-apparently
cache_factory = {}


def get_cache_factory(cache_type):
    """
    Helper to only return a single instance of a cache
    As of django 1.7, may not be needed.
    """
    from django.core.cache import caches

    if cache_type is None:
        cache_type = 'default'

    if not cache_type in cache_factory:
        cache_factory[cache_type] = caches[cache_type]

    return cache_factory[cache_type]


def django_cache_decorator(time=300, cache_key=None, cache_type=None, should_cache=lambda: True):
    '''

    :param time: time in seconds to cache
    :param cache_key: Custom cache key
    :param cache_type: Specify which Django cache type you'd like to use
    :param should_cache: function to dynamically enable/disable cache
    :return:
    '''
    if cache_type is None:
        cache_type = 'default'

    cache = get_cache_factory(cache_type)
    if not cache_key:
        cache_key = None

    def decorator(fn):
        def wrapper(*args, **kwargs):
            if not should_cache():
                return fn(*args, **kwargs)

            # Inner scope variables are read-only so we set a new var
            _cache_key = cache_key

            if not _cache_key:
                _cache_key = cache_get_key(fn.__name__, *args, **kwargs)

            result = cache.get(_cache_key)

            if not result:
                result = fn(*args, **kwargs)
                cache.set(_cache_key, result, time)

            return result

        return wrapper

    return decorator
