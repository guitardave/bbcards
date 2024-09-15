from datetime import datetime


def copyright_year(request):
    return {'copyright_year': datetime.strftime(datetime.now(), '%Y')}
