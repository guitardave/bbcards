from django.http import JsonResponse


def error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as e:
            return JsonResponse('TypeError: %s' % e, safe=False)
        except ValueError as e:
            return JsonResponse('ValueError: %s' % e, safe=False)
        except Exception as e:
            return JsonResponse('Error: %s' % e, safe=False)
    return wrapper
