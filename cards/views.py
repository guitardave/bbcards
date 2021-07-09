from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)

class CardSetCreate(CreateView):
    model = CardSet
    form_class = CardSetForm
    template_name = 'cardset-form.html'
    
    
class CardCreate(CreateView):
    model = Card
    form_class = CardForm
    template_name = 'card-form.html'
    
    
class CardsView(ListView):
    model = Card
    template_name = 'card-list.html'
    
    def get_queryset(self):
        return Card.objects.all().order_by(card_set)
    
    def get_context_data(self, **kwargs):
        super(CardsView, self).get_context_data(**kwargs)
        context['set'] = CardSet.objects.get(card_set)