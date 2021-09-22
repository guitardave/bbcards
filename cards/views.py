from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from .forms import CardSetForm, CardForm
from .models import Card, CardSet


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
    fields = "__all__"


class CardCreate(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'cards/card-form.html'
    
    
class CardsView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'
    
    def get_queryset(self):
        if self.kwargs.get('id'):
            return Card.objects.filter(card_set_id=self.kwargs.get('id')).order_by('card_set_id__year')
        else:
            return Card.objects.all().order_by('card_set_id__year')


class CardsViewPLayer(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'

    def get_queryset(self):
        if self.kwargs.get('id'):
            return Card.objects.filter(player_id_id=self.kwargs.get('id')).order_by('card_set_id__year')
        else:
            return Card.objects.all().order_by('card_set_id__year')


class CardsDetail(DetailView):
    model = Card
    template_name = 'cards/card-detail.html'

    def get_queryset(self):
        return Card.objects.get(pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        context = {'title': 'Card Detail'}
        return render(request, self.template_name, context)


class CardUpdate(LoginRequiredMixin, UpdateView):
    model = Card
    template_name = 'cards/card-form.html'
    fields = '__all__'


def home(request):
    context = {'title': 'Cards Home'}
    return render(request, 'cards/home.html', context)
