from datetime import datetime


def cards_count_ctx(request):
    return {'n': 25}


def copyright_year_ctx(request):
    return {'copyright_year': datetime.strftime(datetime.now(), '%Y')}
