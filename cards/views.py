import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from players.models import Player
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm, CardCreateSetForm
from .models import Card, CardSet


def get_card_set_list():
    return CardSet.objects.all().order_by('year', 'card_set_name')


@login_required(login_url='/users/')
def card_set_create_async(request):
    message = ''
    if request.method == 'POST':
        set_year = request.POST['year']
        set_name = request.POST['card_set_name']
        full_set_name = f'{set_year} {set_name}'
        check = CardSet.objects.filter(card_set_name=set_name, year=set_year)
        if not check.exists():
            form = CardSetForm(request.POST)
            if form.is_valid():
                form.save()
                message = f'<i class="fa fa-check"></i> {full_set_name} has been added'
        else:
            message = f'<i class="fa fa-remove"></i> {full_set_name} already exists'
    return render(request, 'cards/cardset-list-card-partial.html',
                  {
                      'cards': get_card_set_list(),
                      'title': 'Card Sets',
                      'c_message': message
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
    context = {
        'cards': get_card_set_list(),
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
        return render(request, 'cards/cardset-list-tr-partial.html', {'card': obj, 'success': True})
    context = {'form': CardSetForm(instance=obj), 'obj': obj, 'card_title': 'Update Card Set', 'loaded': datetime.datetime.now()}
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
        return Card.objects.all().order_by('-id')[:50]

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'Last 50 Cards'
        data['cards'] = self.get_queryset()
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
        return Card.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'All Cards'
        data['cards'] = self.get_queryset()
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
        form = CardUpdateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'cards/card-list-tr-partial.html', {'card': obj, 'success': True})
    context = {
        'form': CardUpdateForm(instance=obj), 'obj': obj,
        'card_title': 'Update Card',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
def card_create_async(request):
    if request.method == 'POST':
        form = CardCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card has been created')
    cards = Card.objects.all()
    return render(request, 'cards/card-list-table-partial.html', {'cards': cards})


@login_required(login_url='/users/')
def card_form_refresh(request):
    context = {'card_title': 'Add Card', 'form': CardCreateForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/card-form.html', context)
