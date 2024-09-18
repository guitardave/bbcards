import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
from django.views.generic import ListView
from .models import Player
from .forms import PlayerForm


# @cache_page(60*5)
def player_list(request):
    players = Player.list_all.all()
    context = {
        'title': 'Player List',
        'rs': players,
        'form': PlayerForm,
        'loaded': datetime.datetime.now(),
        'card_title': 'Add Player'
    }
    return render(request, 'players/player_list.html', context)


@login_required(login_url="/users/")
def player_add_async(request):
    success = False
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
                success = True
                message = f'<i class="fa fa-check"></i> {f_name} {l_name} entered successfully'
        else:
            message = f'<i class="fa fa-remove"></i> {f_name} {l_name} already exists'
    players = Player.list_all.all()
    new_id = Player.objects.last().id
    context = {
        'title': 'Player List',
        # 'p_success': success,
        'rs': players,
        'new_id': new_id,
        'message': message
    }
    # context = {'p': obj, 'success': success, 'message': message}
    return render(request, 'players/player_list_card_partial.html', context)


@login_required(login_url="/users/")
def player_update_async(request, pk: int):
    player = Player.objects.get(pk=pk)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            t_message = '<i class="fa fa-check"></i>'
        else:
            t_message = '<i class="fa fa-remove"></i> Error'
        return render(request, 'players/player_list_tr_partial.html',
                      {'p': player, 'success': True, 't_message': t_message})
    context = {
        'form': PlayerForm(instance=player),
        'obj': player,
        'card_title': 'Update Player',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'players/player_form.html', context)


@login_required(login_url='/users/')
def player_form_refresh(request):
    context = {'card_title': 'Add Player', 'loaded': datetime.datetime.now(), 'form': PlayerForm}
    return render(request, 'players/player_form.html', context)
