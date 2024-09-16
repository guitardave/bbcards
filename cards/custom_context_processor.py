from datetime import datetime


def copyright_year_ctx(request):
    return {'copyright_year': datetime.strftime(datetime.now(), '%Y')}
