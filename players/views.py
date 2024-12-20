import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from cards.models import Card
from decorators.my_decorators import error_handling
from .models import Player
from .forms import PlayerForm


def player_list_count(p_list: list) -> list[dict]:
    players = []
    for player in p_list:
        p_count = Card.objects.filter(player_id_id=player.id).count()
        if p_count > 0:
            players.append(dict(player=player, count=p_count))
    return players


# @cache_page(60*5)
@error_handling
def player_list(request, n_list: int = 0):
    if n_list == 0:
        players = Player.list_no_ignore.all()
    elif n_list == 99:
        players = Player.list_ignore.all()
    else:
        players = Player.objects.all().order_by('-id')[:n_list]
    context = {
        'title': 'Player List',
        'rs': player_list_count(players),
        'form': PlayerForm,
        'loaded': timezone.now(),
        'card_title': 'Add Player'
    }
    return render(request, 'players/player_list.html', context)


@login_required(login_url="/users/")
@error_handling
def player_add_async(request):
    message = ''
    if request.method == 'POST':
        f_name = request.POST['player_fname']
        l_name = request.POST['player_lname']
        check = Player.objects.filter(
            player_fname__iexact=f_name,
            player_lname__iexact=l_name
        )
        if not check.exists():
            form = PlayerForm(request.POST)
            if form.is_valid():
                form.save()
                message = f'<i class="fa fa-check"></i> {f_name} {l_name} entered successfully'
        else:
            message = f'<i class="fa fa-remove"></i> {f_name} {l_name} already exists'
    players = Player.list_all.all()
    new_id = Player.objects.last().id
    context = {
        'title': 'Player List',
        'rs': [{'player': p, 'count': Card.objects.filter(player_id_id=p.id).count()} for p in players],
        'new_id': new_id,
        'message': message
    }
    return render(request, 'players/player_list_card_partial.html', context)


@login_required(login_url="/users/")
@error_handling
def player_update_async(request, pk: int):
    player = Player.objects.get(pk=pk)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            t_message = '<i class="fa fa-check"></i>'
        else:
            t_message = '<i class="fa fa-remove"></i> Error'
        return render(
            request,
            'players/player_list_tr_partial.html',
            {'p':
                {
                    'player': Player.objects.get(pk=pk),
                    'count': Card.objects.filter(player_id_id=pk).count()
                },
                'success': True,
                't_message': t_message
            }
        )
    context = {
        'form': PlayerForm(instance=player),
        'obj': player,
        'card_title': 'Update Player',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'players/player_form.html', context)


@login_required(login_url='/users/')
@error_handling
def player_form_refresh(request):
    context = {'card_title': 'Add Player', 'loaded': datetime.datetime.now(), 'form': PlayerForm}
    return render(request, 'players/player_form.html', context)


@login_required(login_url='/users/')
@csrf_exempt
@error_handling
def player_delete_async(request, player_id: int):
    message = ''
    obj = Player.objects.filter(id=player_id)
    if obj.exists():
        obj.delete()
        message = 'Player deleted successfully'
    players = Player.list_all.all()
    context = {
        'title': 'Player List',
        'rs': [{'player': p, 'count': Card.objects.filter(player_id_id=p.id).count()} for p in players],
        'message': message
    }
    return render(request, 'players/player_list_card_partial.html', context)
