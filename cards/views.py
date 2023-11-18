from django.shortcuts import HttpResponseRedirect, redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (ListView, DetailView, CreateView, UpdateView)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm, CardCreateSetForm
from .models import Card, CardSet


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
    ordering = 'year'

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
        data['title'] = 'Update - ' + '{} {}'.format(obj.year, obj.card_set_name)
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


def pagination(request, qs):
    paginator = Paginator(qs, 50)
    page = request.GET.get('page', 1)
    try:
        cards = paginator.page(page)
    except PageNotAnInteger:
        cards = paginator.page(1)
    except EmptyPage:
        cards = paginator.page(paginator.num_pages)
    return cards


def card_list_view(request, qs):
    cards = pagination(request, qs)
    context = {'title': 'Cards List', 'cards': cards}
    return render(request, 'cards/card-list.html', context)


def card_set_list(request):
    c_list = Card.objects.all().order_by('card_set_id__slug')
    return card_list_view(request, c_list)


def card_list(request, slug):
    c_list = Card.objects.filter(card_set_id__slug=slug).order_by('card_set_id__slug')
    return card_list_view(request, c_list)


def cards_list_player(request, slug):
    c_list = Card.objects.filter(player_id__slug=slug).order_by('card_set_id__slug')
    return card_list_view(request, c_list)


class CardsListView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    paginate_by = 50
    context_object_name = 'cards'
    ordering = 'card_set_id__slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super(CardsListView, self).get_context_data(**kwargs)
        data['title'] = 'Cards List'
        data['cards'] = self.get_queryset()
        return data


class CardsView(CardsListView):
    def get_queryset(self):
        return Card.objects.filter(card_set_id__slug=self.kwargs.get('slug')).order_by('card_set_id__slug')


class CardsViewPLayer(CardsListView):
    def get_queryset(self):
        return Card.objects.filter(player_id__slug=self.kwargs.get('slug')).order_by('card_set_id__slug')


class CardsDetail(DetailView):
    model = Card
    template_name = 'cards/card-detail.html'

    def get_context_data(self, **kwargs):
        obj = Card.objects.get(pk=self.kwargs.get('pk'))
        data = super(CardsDetail, self).get_context_data(**kwargs)
        data['title'] = 'Card Detail - ' + obj.card_num
        data['object'] = obj
        return data


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
