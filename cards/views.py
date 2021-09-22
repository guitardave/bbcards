from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm
from .models import Card, CardSet
from players.models import Player


def home(request):
    context = {'title': 'Cards Home'}
    return render(request, 'cards/home.html', context)


class CardSetCreate(LoginRequiredMixin, CreateView):
    model = CardSet
    form_class = CardSetForm
    template_name = 'cards/cardset-form.html'


class CardSetList(ListView):
    model = CardSet
    template_name = 'cards/cardset-list.html'
    context_object_name = 'cards'
    paginate_by = 50

    def get_queryset(self):
        return CardSet.objects.all().order_by('card_set_name')


class CardSetUpdate(LoginRequiredMixin, UpdateView):
    model = CardSet
    template_name = 'cards/cardset-form.html'
    form_class = CardUpdateForm


class CardCreate(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardCreateForm
    template_name = 'cards/card-form.html'


class CardsView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.all().order_by('card_set_id__year').\
                order_by('card_set_id__card_set_name').order_by('player_id__player_lname')


class CardsViewAll(CardsView):
    def get_queryset(self):
        if self.kwargs.get('slug'):
            return Card.objects.filter(card_set_id__slug=self.kwargs.get('slug')).order_by('card_set_id__year').\
                order_by('card_set_id__card_set_name').order_by('player_id__player_lname')


class CardsViewPLayer(CardsView):
    def get_queryset(self):
        if self.kwargs.get('slug'):
            return Card.objects.filter(player_id__slug=self.kwargs.get('slug')).order_by('card_set_id__year').\
                order_by('card_set_id__card_set_name').order_by('player_id__player_lname')


class CardsDetail(DetailView):
    model = Card
    template_name = 'cards/card-detail.html'


class CardUpdate(LoginRequiredMixin, UpdateView):
    model = Card
    template_name = 'cards/card-form.html'
    form_class = CardUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs


def card_search(request):
    context = {'title': 'Card Search'}
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            cards = Card.objects.filter(card_set_id__card__card_subset__icontains=request.POST['search'])
            context['cards'] = cards
            context['form'] = SearchForm()
        return render(request, 'cards/card-search.html', context)
    else:
        form = SearchForm()
        context['form'] = form
    return render(request, 'cards/card-search.html', context)
