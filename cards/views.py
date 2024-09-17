import datetime
import os

import boto3
import openpyxl
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.contrib import messages
from openpyxl.workbook import Workbook

from players.models import Player
from .forms import CardSetForm, CardUpdateForm, CardCreateForm
from .models import Card, CardSet, CardListExport


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
                      'rs': cards,
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
        'rs': cards,
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
        data['rs'] = self.get_queryset()
        data['form'] = CardCreateForm()
        data['card_title'] = 'Add Card'
        data['loaded'] = datetime.datetime.now()
        self.request.session['rs'] = card_list_dict(data['rs'])
        data['rs_dict'] = self.request.session['rs'] if 'rs' in self.request.session else []
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
        data['rs'] = self.get_queryset()
        data['form'] = CardCreateForm
        data['card_title'] = 'Add Card'
        data['loaded'] = datetime.datetime.now()
        self.request.session['rs'] = card_list_dict(data['rs'])
        data['rs_dict'] = self.request.session['rs'] if 'rs' in self.request.session else []
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
        data['rs'] = self.get_queryset()
        data['card_set'] = card_set
        data['form'] = CardCreateForm(**{'set': card_set.slug})
        data['card_title'] = 'Add Card - by Card Set'
        data['loaded'] = datetime.datetime.now()
        self.request.session['rs'] = card_list_dict(data['rs'])
        data['rs_dict'] = self.request.session['rs'] if 'rs' in self.request.session else []
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
        data['rs'] = self.get_queryset()
        data['player'] = player
        data['form'] = CardCreateForm(**{'player': player.slug})
        data['card_title'] = 'Add Card - by Player'
        data['loaded'] = datetime.datetime.now()
        self.request.session['rs'] = card_list_dict(data['rs'])
        data['rs_dict'] = self.request.session['rs'] if 'rs' in self.request.session else []
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
@csrf_exempt
def card_delete_async(request, pk: int):
    c_message, cards, player = None, None, None
    obj = Card.objects.filter(pk=pk)
    if obj.exists():
        cards = Card.objects.filter(player_id_id=obj[0].player_id_id)
        player = Player.objects.get(id=obj[0].player_id_id)
        obj.delete()
        c_message = 'Item deleted successfully'
    context = {
        'rs': cards if cards else Card.last_50.all(),
        'c_message': c_message,
        'title': 'Last 50 Cards' if not player else f'{player.player_fname} {player.player_lname}'
    }
    return render(request, 'cards/card-list-card-partial.html', context)


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
        'rs': cards,
        # 't_message': t_message
    }
    return render(request, 'cards/card-list-card-partial.html', context)


@login_required(login_url='/users/')
def card_form_refresh(request):
    context = {'card_title': 'Add Card', 'form': CardCreateForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
def card_image(request, pk: int):
    obj = Card.objects.get(pk=pk)
    card_string = f'{obj.card_set_id.year} {obj.card_set_id.card_set_name} {obj.card_subset} {obj.card_num}'
    context = {'title': obj.card_image, 'object': obj, 'card_string': card_string}
    return render(request, 'cards/card-image.html', context)


def card_search_rs(search: str):
    return Card.objects.filter(
        Q(card_set_id__card_set_name__icontains=search) |
        Q(card_subset__icontains=search) |
        Q(player_id__player_lname__icontains=search) |
        Q(player_id__player_fname__icontains=search)
    ).order_by(
        'card_set_id__year',
        'card_set_id__card_set_name',
        'player_id__player_lname'
    )


@login_required(login_url='/users/')
def card_search(request):
    cards = []
    search = ''
    if request.method == 'POST':
        search = request.POST['search']
        cards = card_search_rs(search)
        request.session['rs'] = card_list_dict(cards)
    context = {
        'rs': cards,
        'title': f'Search "{search}"',
        'form': CardCreateForm,
        'search': search,
        'rs_dict': request.session['rs'] if 'rs' in request.session else []
    }
    return render(request, 'cards/card-list.html', context)


class ExportScriptsExcel:
    DEST_DIR = 'static/bbcards/export_data/'

    def __init__(self, rs: list[dict[str, str]], file_name: str) -> None:
        self.file_name = file_name
        self.rs = rs

    def create_file(self) -> Workbook:
        wb = openpyxl.Workbook()
        wb.save(self.file_name)
        return wb

    def populate_excel_file(self) -> Workbook:
        rs = self.rs
        self.create_file()
        wb = openpyxl.load_workbook(self.file_name)
        ws = wb.active
        for i, s in enumerate(rs):
            ws.cell(i + 1, 1).value = s['player_name']
            ws.cell(i + 1, 2).value = s['year']
            ws.cell(i + 1, 3).value = s['set_name']
            ws.cell(i + 1, 4).value = s['info']
            ws.cell(i + 1, 5).value = s['num']
        wb.save(self.file_name)
        return wb

    def upload_excel(self) -> None:
        wb = self.populate_excel_file()
        client = boto3.Session(os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY')).resource('s3')
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        result = client.Bucket(bucket).upload_file(self.file_name, self.DEST_DIR+self.file_name)
        print(result)
        return result

    def run_process(self) -> None:
        self.upload_excel()
        os.remove(self.file_name)


def export_list_save(request, file_name: str):
    export = CardListExport(user_id=request.user.id, file_name=file_name)
    export.save()


def card_list_dict(cards) -> list[dict]:
    return [
            {
                'player_name': c.player_id.player_fname + ' ' + c.player_id.player_lname,
                'year': c.card_set_id.year,
                'set_name': c.card_set_id.card_set_name,
                'info': c.card_subset,
                'num': c.card_num
            } for c in cards]


def card_list_export(rs: list[dict]) -> str:
    file_name = ''
    if len(rs) > 0:
        f_date = datetime.datetime.strftime(datetime.datetime.today(), '%m_%d_%Y__%H_%M_%S')
        file_name = f"bbcards_card_list_export_{str(f_date)}.xlsx"
        xl = ExportScriptsExcel(rs, file_name)
        # dest_file = xl.DEST_DIR + file_name
        xl.run_process()
    return file_name


@login_required(login_url='/users/')
@csrf_exempt
def card_list_export_vw(request):
    result = card_list_export(request.session['rs']) if 'rs' in request.session else ''
    if len(result) > 0:
        export_list_save(request, result)
        request.session['rs'] = None
    context = {
        'xport_result': result,
        'xport_url': 'https://jojodave.s3.amazonaws.com/static/bbcards/export_data/'+result
    }
    return render(request, 'cards/card-list-export-msg-partial.html', context)
