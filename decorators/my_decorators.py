from django.http import JsonResponse


def error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as e:
            return JsonResponse('TypeError: %s' % e)
        except ValueError as e:
            JsonResponse('ValueError: %s' % e)
        except Exception as e:
            JsonResponse('Error: %s' % e)
    return wrapper
