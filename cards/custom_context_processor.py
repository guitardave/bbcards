from datetime import datetime

from django.conf import settings

from cards.models import CardSet
from players.models import Player


def cards_count_ctx(request):
    return {'n': settings.DEFAULT_LIMIT}


def card_sets_list_ctx(request):
    return [(x.id, x.__str__()) for x in CardSet.objects.all().order_by('year', 'card_set_name')]


def player_list_ctx(request):
    return [(x.id, x.__str__()) for x in Player.objects.all().order_by('player_lname', 'player_fname')]


def copyright_year_ctx(request):
    return {'copyright_year': datetime.strftime(datetime.now(), '%Y')}
