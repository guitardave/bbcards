from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm, CardCreateSetForm
from .models import Card, CardSet
from players.models import Player


def home(request):
    context = {'title': 'Cards Home'}
    return render(request, 'cards/home.html', context)


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


class CardSetList(ListView):
    model = CardSet
    template_name = 'cards/cardset-list.html'
    context_object_name = 'cards'
    paginate_by = 50

    def get_queryset(self):
        return CardSet.objects.all().order_by('year')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardSetList, self).get_context_data(**kwargs)
        data['title'] = 'Card Sets'
        data['cards'] = self.get_queryset()
        return data


class CardSetUpdate(LoginRequiredMixin, UpdateView):
    model = CardSet
    template_name = 'cards/cardset-form.html'
    form_class = CardSetForm
    context_object_name = 'out'

    def get_context_data(self, **kwargs):
        obj = CardSet.objects.get(slug=self.kwargs['slug'])
        data = super(CardSetUpdate, self).get_context_data(**kwargs)
        data['title'] = 'Update - ' + obj.card_set_name
        data['out'] = self.context_object_name
        return data


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

    """
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            obj = Card.objects.latest('id')
            messages.success(request, 'Card Created Successfully')
            return redirect('cards:card-det', obj.id)

    def get(self, request, *args, **kwargs):
        context = {'title': 'Enter new card', 'form': self.form_class}
        return render(request, self.template_name, context)
    """


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
        data['title'] = 'Add Card - ' + obj.card_set_name
        data['out'] = self.context_object_name
        return data


class CardsView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(card_set_id__slug=self.kwargs.get('slug')).order_by('card_set_id__slug')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardsView, self).get_context_data(**kwargs)
        data['title'] = 'Cards List'
        data['cards'] = self.get_queryset()
        return data


class CardsViewAll(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.all().order_by('card_set_id__slug')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardsViewAll, self).get_context_data(**kwargs)
        data['title'] = 'Cards List'
        data['cards'] = self.get_queryset()
        return data


class CardsViewPLayer(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(player_id__slug=self.kwargs.get('slug')).order_by('card_set_id__slug')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardsViewPLayer, self).get_context_data(**kwargs)
        data['title'] = 'Cards List'
        data['cards'] = self.get_queryset()
        return data

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
        cards = []
        if form.is_valid():
            cards.append(dict(Card.objects.filter(card_set_id__card__card_subset__icontains=request.POST['search'])))
            cards.append(dict(Card.objects.filter(card_set_id__card_set_name__icontains=request.POST['search'])))
            context['cards'] = cards
            context['form'] = SearchForm()
        return render(request, 'cards/card-search.html', context)
    else:
        form = SearchForm()
        context['form'] = form
    return render(request, 'cards/card-search.html', context)
