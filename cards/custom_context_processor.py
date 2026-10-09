from datetime import datetime

from django.conf import settings


def cards_count_ctx(request):
    return {'n': settings.DEFAULT_LIMIT}


def copyright_year_ctx(request):
    return {'copyright_year': datetime.strftime(datetime.now(), '%Y')}
