from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from . import forms
from . import models


class CardSetCreate(CreateView):
    model = CardSet
    form_class = CardSetForm
    template_name = 'cardset-form.html'


class CardSetList(ListView):
    model = CardSet
    template_name = 'cards/home.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return CardSet.objects.all().order_by('card_set_name')

    
class CardCreate(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'card-form.html'

    def post(self, request, *args, **kwargs):
        context = {'title': 'Create Card'}
        if kwarg.get('id'):
            form = self.form_class(request.POST, instance=kwargs.get('id') or None)
        else:
            form = self.form_class(request.POST or None)
        return reverse('cards:')


    def get(self, request, *args, **kwargs):
        context = {'title': 'Create Card'}
        if kwargs.get('id'):
            form = CardForm(instance=kwargs.get('id'))
        else:
            form = CardForm()

        context['form'] = form
        return render(request, self.template_name, context)
    
    
class CardsView(ListView):
    model = Card
    template_name = 'card-list.html'
    
    def get_queryset(self):
        return Card.objects.all().order_by(card_set)
    
    def get_context_data(self, **kwargs):
        super(CardsView, self).get_context_data(**kwargs)
        context['set'] = CardSet.objects.get(card_set)


class CardsDetail(DetailView):
    model = CardSet
    template_name = 'card-detail.html'

    def get_queryset(self):
        return Card.objects.get(pk=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):
        context = {'title': 'Card Detail'}
        return render(request, self.template_name, context)