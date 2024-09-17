def error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TypeError as e:
            m = 'TypeError: %s' % e
        except ValueError as e:
            m = 'ValueError: %s' % e
        except Exception as e:
            m = 'Error: %s' % e
    return wrapper
