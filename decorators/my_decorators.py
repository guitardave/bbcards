import functools
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse

logger = logging.getLogger(__name__)


def error_handling(func):
    """
    Catch unhandled exceptions in a view, log the traceback server-side, and return a JSON
    error with a generic message and a matching status code. Exception text is never sent to the client.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (Http404, ObjectDoesNotExist):
            logger.warning('Not found in %s', func.__name__, exc_info=True)
            return JsonResponse({'error': 'Not found.'}, status=404)
        except (TypeError, ValueError):
            logger.exception('Bad input in %s', func.__name__)
            return JsonResponse({'error': 'Invalid request.'}, status=400)
        except Exception:
            logger.exception('Unhandled error in %s', func.__name__)
            return JsonResponse({'error': 'Something went wrong. Please try again.'}, status=500)
    return wrapper
