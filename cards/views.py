import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib import messages

from players.models import Player
from .forms import CardSetForm, CardUpdateForm, CardCreateForm
from .models import Card, CardSet


def get_card_set_list():
    return CardSet.objects.all().order_by('year', 'card_set_name')


@login_required(login_url='/users/')
def card_set_create_async(request):
    c_message = ''
    if request.method == 'POST':
        set_year = request.POST['year']
        set_name = request.POST['card_set_name']
        full_set_name = f'{set_year} {set_name}'
        check = CardSet.objects.filter(card_set_name=set_name, year=set_year)
        if not check.exists():
            form = CardSetForm(request.POST)
            if form.is_valid():
                form.save()
                c_message = f'<i class="fa fa-check"></i> {full_set_name} has been added'
        else:
            c_message = f'<i class="fa fa-remove"></i> {full_set_name} already exists'
    cards = get_card_set_list()
    new_id = Card.objects.last().id
    return render(request, 'cards/cardset-list-card-partial.html',
                  {
                      'cards': cards,
                      'rs_len': len(cards),
                      'new_id': new_id,
                      'title': 'Card Sets',
                      'c_message': c_message
                  }
                  )


def card_set_list(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card set has been created')
        return redirect('cards:cardsets')
    form = CardSetForm
    cards = get_card_set_list()
    context = {
        'cards': cards,
        'rs_len': len(cards),
        'form': form,
        'title': 'Card Sets',
        'card_title': 'Add Card Set',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'cards/cardset-list.html', context)


@login_required(login_url="/users/")
def card_set_update_async(request, pk: int):
    obj = CardSet.objects.get(pk=pk)
    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            t_message = '<i class="fa fa-check"></i>'
        else:
            t_message = '<i class="fa fa-remove"></i> Error'
        context = {'card': obj, 'success': True, 't_message': t_message}
        return render(request, 'cards/cardset-list-tr-partial.html', context)
    context = {
        'form': CardSetForm(instance=obj),
        'obj': obj,
        'card_title': 'Update Card Set',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'cards/cardset-form.html', context)


@login_required(login_url='/users/')
def card_set_form_refresh(request):
    context = {'card_title': 'Add Card Set', 'form': CardSetForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/cardset-form.html', context)


class CardsListView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    context_object_name = 'cards'
    ordering = 'card_set_id__slug'

    def get_queryset(self):
        return Card.last_50.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'Last 50 Cards'
        data['cards'] = self.get_queryset()
        data['rs_len'] = self.get_queryset().count()
        data['form'] = CardCreateForm()
        data['card_title'] = 'Add Card'
        data['loaded'] = datetime.datetime.now()
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Card has been created')
        return redirect('cards:card-list-50')


class CardsViewAll(CardsListView):
    def get_queryset(self):
        return Card.list_all.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'All Cards'
        data['cards'] = self.get_queryset()
        data['rs_len'] = len(data['cards'])
        data['form'] = CardCreateForm
        data['card_title'] = 'Add Card'
        data['loaded'] = datetime.datetime.now()
        return data


class CardsViewSet(CardsListView):
    def get_object(self):
        return CardSet.objects.get(slug=self.kwargs.get('slug'))

    def get_card_set(self):
        card_set = self.get_object()
        return f'{card_set.year} {card_set.card_set_name}'

    def get_queryset(self):
        return Card.objects.filter(card_set_id__slug=self.kwargs.get('slug'))

    def get_context_data(self, *, object_list=None, **kwargs):
        card_set = self.get_object()
        data = super(CardsViewSet, self).get_context_data(**kwargs)
        data['title'] = f'{self.get_card_set()}'
        data['cards'] = self.get_queryset()
        data['rs_len'] = self.get_queryset().count()
        data['card_set'] = card_set
        data['form'] = CardCreateForm(**{'set': card_set.slug})
        data['card_title'] = 'Add Card - by Card Set'
        data['loaded'] = datetime.datetime.now()
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request,
                             f'Card for {self.get_card_set()} has been created')
        return redirect('cards:card-list-set', slug=self.kwargs.get('slug'))


class CardsViewPlayer(CardsListView):
    def get_queryset(self):
        return Card.objects.filter(player_id__slug=self.kwargs.get('slug'))

    def get_object(self):
        return Player.objects.get(slug=self.kwargs.get('slug'))

    def get_player_name(self):
        player = self.get_object()
        return f'{player.player_fname} {player.player_lname}'

    def get_context_data(self, *, object_list=None, **kwargs):
        player = self.get_object()
        data = super(CardsViewPlayer, self).get_context_data(**kwargs)
        data['title'] = f'{self.get_player_name()}'
        data['cards'] = self.get_queryset()
        data['rs_len'] = self.get_queryset().count()
        data['player'] = player
        data['form'] = CardCreateForm(**{'player': player.slug})
        data['card_title'] = 'Add Card - by Player'
        data['loaded'] = datetime.datetime.now()
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request,
                             f'Card for {self.get_player_name()} has been created')
        return redirect('cards:card-list-player', slug=self.kwargs.get('slug'))


@login_required(login_url="/users/")
def card_update_async(request, pk: int):
    obj = Card.objects.get(pk=pk)
    if request.method == 'POST':
        success = False
        form = CardUpdateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            success = True
            t_message = '<i class="fa fa-check"></i>'
        else:
            t_message = '<i class="fa fa-remove"></i> Error'
        return render(
            request,
            'cards/card-list-tr-partial.html',
            {'card': Card.objects.get(pk=pk), 'success': success, 't_message': t_message}
        )
    context = {
        'form': CardUpdateForm(instance=obj), 'obj': obj,
        'card_title': 'Update Card',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
def card_create_async(request):
    # t_message = None
    new_id = None
    if request.method == 'POST':
        form = CardCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            new_id = Card.objects.last().id
            # t_message = '<i class="fa fa-check"></i> Success'
    cards = Card.last_50.all()
    context = {
        'title': 'Last 50 Cards',
        'new_id': new_id,
        'cards': cards,
        'rs_len': cards.count(),
        # 't_message': t_message
    }
    return render(request, 'cards/card-list-table-partial.html', context)


@login_required(login_url='/users/')
def card_form_refresh(request):
    context = {'card_title': 'Add Card', 'form': CardCreateForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
def card_search(request):
    cards = []
    search = ''
    if request.method == 'POST':
        search = request.POST['search']
        cards = Card.objects.filter(
            Q(card_set_id__card_set_name__icontains=search) |
            Q(card_subset__icontains=search) |
            Q(player_id__player_lname__icontains=search) |
            Q(player_id__player_fname__icontains=search)
        ).order_by('card_set_id__year', 'card_set_id__card_set_name', 'player_id__player_lname')
    context = {'cards': cards, 'rs_len': len(cards), 'title': f'Search "{search}"', 'form': CardCreateForm}
    return render(request, 'cards/card-list.html', context)
