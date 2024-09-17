import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import ListView
from .models import Player
from .forms import PlayerForm


class PlayerList(ListView):
    model = Player
    template_name = 'players/player_list.html'
    context_object_name = 'players'
    paginate_by = 30
    ordering = 'player_lname'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(PlayerList, self).get_context_data(**kwargs)
        data['title'] = 'Player List'
        data['rs'] = self.get_queryset()
        data['form'] = PlayerForm()
        data['loaded'] = datetime.datetime.now()
        data['card_title'] = 'Add Player'
        return data

    def post(self, *args, **kwargs):
        form = PlayerForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Your player was successfully saved.')
            return redirect('players:players-home')


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
