"""
Security decorators for API endpoints
"""
import functools
import hashlib
import time
from django.core.cache import cache
from django.http import JsonResponse


def rate_limit(max_requests=10, window_seconds=60, key_prefix='rate_limit'):
    """
    Rate limiting decorator for API endpoints
    
    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds
        key_prefix: Prefix for cache key
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f"{key_prefix}:{hashlib.md5(client_ip.encode()).hexdigest()}"

            request_count = cache.get(cache_key, 0)

            if request_count >= max_requests:
                return JsonResponse({
                    'error': 'rate_limit_exceeded',
                    'message': 'Quá nhiều yêu cầu. Vui lòng thử lại sau.',
                    'retry_after': window_seconds
                }, status=429)

            cache.set(cache_key, request_count + 1, window_seconds)

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def rate_limit_class(max_requests=10, window_seconds=60, key_prefix='rate_limit'):
    """
    Rate limiting decorator for class-based views
    """

    def decorator(cls):
        original_dispatch = cls.dispatch

        @functools.wraps(original_dispatch)
        def dispatch(self, request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f"{key_prefix}:{hashlib.md5(client_ip.encode()).hexdigest()}"

            request_count = cache.get(cache_key, 0)

            if request_count >= max_requests:
                return JsonResponse({
                    'error': 'rate_limit_exceeded',
                    'message': 'Quá nhiều yêu cầu. Vui lòng thử lại sau.',
                    'retry_after': window_seconds
                }, status=429)

            cache.set(cache_key, request_count + 1, window_seconds)

            return original_dispatch(self, request, *args, **kwargs)

        cls.dispatch = dispatch
        return cls

    return decorator


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def require_origin(allowed_origins=None):
    """
    Decorator to check Origin header for API endpoints
    This helps prevent unauthorized cross-origin requests
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            origin = request.META.get('HTTP_ORIGIN', '')
            host = request.get_host()

            if allowed_origins:
                if origin and origin not in allowed_origins:
                    return JsonResponse({
                        'error': 'forbidden',
                        'message': 'Origin không được phép'
                    }, status=403)
            else:
                if origin:
                    from urllib.parse import urlparse
                    parsed = urlparse(origin)
                    if parsed.netloc and parsed.netloc != host:
                        pass

            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_origin_class(allowed_origins=None):
    """
    Origin check decorator for class-based views
    """

    def decorator(cls):
        original_dispatch = cls.dispatch

        @functools.wraps(original_dispatch)
        def dispatch(self, request, *args, **kwargs):
            origin = request.META.get('HTTP_ORIGIN', '')
            referer = request.META.get('HTTP_REFERER', '')
            host = request.get_host()

            if allowed_origins:
                if origin and origin not in allowed_origins:
                    return JsonResponse({
                        'error': 'forbidden',
                        'message': 'Origin không được phép'
                    }, status=403)

            return original_dispatch(self, request, *args, **kwargs)

        cls.dispatch = dispatch
        return cls

    return decorator
