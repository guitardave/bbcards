from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from players.models import Player
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm, CardCreateSetForm
from .models import Card, CardSet


class CardSetCreate(LoginRequiredMixin, CreateView):
    model = CardSet
    form_class = CardSetForm
    template_name = 'cards/cardset-form.html'
    context_object_name = 'out'

    def get_context_data(self, **kwargs):
        data = super(CardSetCreate, self).get_context_data(**kwargs)
        data['out'] = self.context_object_name
        data['title'] = 'Create Card Set'
        return data


def card_set_create(request):
    if request.method == 'POST':
        form = CardCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request, 'cards/cardset-list-table-partial.html', {'cards': CardSet.objects.all()})


def card_set_list(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card set has been created')
            return redirect('cards:cardsets')
    form = CardSetForm
    context = {'cards': CardSet.objects.all().order_by('year', 'card_set_name'), 'form': form, 'title': 'Card Sets'}
    return render(request, 'cards/cardset-list.html', context)


class CardSetList(ListView):
    model = CardSet
    template_name = 'cards/cardset-list.html'
    context_object_name = 'cards'
    paginate_by = 50
    ordering = 'year'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardSetList, self).get_context_data(**kwargs)
        data['title'] = 'Card Sets'
        data['cards'] = self.get_queryset()
        return data


def card_set_update_async(request, pk: int):
    obj = CardSet.objects.get(pk=pk)
    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'cards/cardset-list-tr-partial.html', {'card': obj, 'success': True})
    form = CardSetForm(instance=obj)
    return render(request, 'cards/cardset-form.html', {'form': form, 'obj': obj})


class CardCreate(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardCreateForm
    template_name = 'cards/card-form.html'
    context_object_name = 'out'

    def get_context_data(self, **kwargs):
        data = super(CardCreate, self).get_context_data(**kwargs)
        data['title'] = 'Enter New Card'
        data['out'] = self.context_object_name
        return data


class CardNewSet(LoginRequiredMixin, CreateView):
    model = Card
    template_name = 'cards/card-form.html'
    form_class = CardCreateSetForm
    context_object_name = 'out'

    def get_form_kwargs(self):
        kwargs = super(CardNewSet, self).get_form_kwargs()
        kwargs['slug'] = self.kwargs['slug']
        return kwargs

    def get_context_data(self, **kwargs):
        obj = CardSet.objects.get(slug=self.kwargs['slug'])
        data = super(CardNewSet, self).get_context_data(**kwargs)
        data['title'] = f'Add Card - {obj.year} {obj.card_set_name}'
        data['out'] = self.context_object_name
        return data


class CardList(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'cards/card-list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(
            card_set_id__slug=self.kwargs['slug']
        ).order_by(
            'card_set_id__year', 'card_set_id__card_set_name', 'card_num'
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        kwargs = {'set': self.kwargs['slug']}
        data['title'] = 'Card List'
        data['form'] = CardCreateForm(**kwargs)
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Card has been created')
            return redirect('cards:card-list')


class CardsListView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    context_object_name = 'cards'
    ordering = 'card_set_id__slug'

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data['title'] = 'All Cards'
        data['cards'] = self.get_queryset()
        data['form'] = CardCreateForm()
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Card has been created')
        return redirect('cards:card-list')


class CardsViewSet(CardsListView):
    def get_card_set(self):
        return CardSet.objects.get(slug=self.kwargs.get('slug'))

    def get_queryset(self):
        return Card.objects.filter(card_set_id__slug=self.kwargs.get('slug')).order_by('card_subset')

    def get_context_data(self, *, object_list=None, **kwargs):
        card_set = self.get_card_set()
        data = super(CardsViewSet, self).get_context_data(**kwargs)
        data['title'] = f'{card_set.year} {card_set.card_set_name}'
        data['cards'] = self.get_queryset()
        data['card_set'] = card_set
        data['form'] = CardCreateForm(**{'set': card_set.slug})
        return data

    def post(self, *args, **kwargs):
        card_set = self.get_card_set()
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request,
                             f'Card for set {card_set.year} {card_set.card_set_name} has been created')
        return redirect('cards:card-list-set', slug=self.kwargs.get('slug'))


class CardsViewPlayer(CardsListView):
    def get_queryset(self):
        return Card.objects.filter(player_id__slug=self.kwargs.get('slug')).order_by('card_set_id__slug')

    def get_player(self):
        return Player.objects.get(slug=self.kwargs.get('slug'))

    def get_context_data(self, *, object_list=None, **kwargs):
        player = self.get_player()
        data = super(CardsViewPlayer, self).get_context_data(**kwargs)
        data['title'] = f'{player.player_fname} {player.player_lname}'
        data['cards'] = self.get_queryset()
        data['player'] = player
        data['form'] = CardCreateForm(**{'player': player.slug})
        return data

    def post(self, *args, **kwargs):
        form = CardCreateForm(self.request.POST)
        if form.is_valid():
            form.save()
            messages.success(self.request,
                             f'Card for player {self.get_player().player_lname} has been created')
        return redirect('cards:card-list-player', slug=self.kwargs.get('slug'))


class CardsDetail(DetailView):
    model = Card
    template_name = 'cards/card-detail.html'

    def get_object(self, *args, **kwargs):
        return Card.objects.get(pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        data = super(CardsDetail, self).get_context_data(**kwargs)
        data['title'] = f''' 
            {obj.card_set_id.year} 
            {obj.card_set_id.card_set_name} 
            {obj.player_id.player_fname} {obj.player_id.player_lname}  
            {'(' + obj.card_subset + ')' if obj.card_subset else ""} 
            #{obj.card_num}
            '''
        data['object'] = obj
        kwargs = {'pk': kwargs.get('pk')}
        data['form'] = CardUpdateForm(instance=obj, **kwargs)
        return data

    def post(self, *args, **kwargs):
        form = CardUpdateForm(self.request.POST, instance=self.get_object(), **kwargs)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Card has been updated')
        return redirect('cards:card-det', pk=kwargs.get('pk'))


class CardUpdate(LoginRequiredMixin, UpdateView):
    model = Card
    template_name = 'cards/card-form.html'
    form_class = CardUpdateForm
    context_object_name = 'out'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs

    def get_context_data(self, **kwargs):
        data = super(CardUpdate, self).get_context_data(**kwargs)
        data['title'] = 'Update Card Details'
        data['out'] = self.context_object_name
        return data


def card_update(request, pk):
    obj = Card.objects.get(pk=pk)
    if request.method == 'POST':
        form = CardUpdateForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return render(request, 'cards/card-list-tr-partial.html', {'card': obj})
    return render(request, 'cards/card-form.html', {'form': CardUpdateForm(instance=obj)})

