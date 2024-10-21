import datetime
from xhtml2pdf import pisa
import os
from typing import Any, List, Dict

import openpyxl
from django.db.models.functions import Cast
from django.utils import timezone
from openpyxl.workbook import Workbook
import boto3
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q, QuerySet, IntegerField
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.contrib import messages

from players.models import Player
from .forms import CardSetForm, CardUpdateForm, CardCreateForm, SearchForm
from .models import Card, CardSet, CardListExport
from decorators.my_decorators import error_handling


@login_required(login_url='/users/')
@error_handling
def card_set_create_async(request):
    c_message = ''
    if request.method == 'POST':
        set_year, set_name, sport = request.POST['year'], request.POST['card_set_name'], request.POST['sport']
        full_set_name = f'{set_year} {set_name} {sport}'
        check = CardSet.objects.filter(card_set_name=set_name, year=set_year, sport=sport)
        if not check.exists():
            form = CardSetForm(request.POST)
            if form.is_valid():
                form.save()
                c_message = f'<i class="fa fa-check"></i> {full_set_name} has been added'
        else:
            c_message = f'<i class="fa fa-remove"></i> {full_set_name} already exists'
    context = {
        'rs': card_list_count(CardSet.all_sets.all()),
        'new_id': Card.objects.last().id,
        'title': 'Card Sets',
        'c_message': c_message
    }
    return render(request, 'cards/cardset-list-card-partial.html', context)


@error_handling
def card_set_load_more(request, page=None):
    if not page:
        page = 1
    out = CardSet.objects.filter()


@error_handling
def card_set_list(request):
    if request.method == 'POST':
        form = CardSetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Card set has been created')
        return redirect('cards:cardsets')
    form = CardSetForm
    card_sets = card_list_count(CardSet.all_sets.all())

    set_count, rs, n_pages = card_list_pagination(request, card_sets)

    context = {
        'rs': rs,
        'form': form,
        'title': 'Card Sets',
        'card_title': 'Add Card Set',
        'set_count': set_count,
        'n_pages': n_pages,
        'loaded': timezone.now()
    }
    return render(request, 'cards/cardset-list.html', context)


@login_required(login_url="/users/")
@error_handling
def card_set_update_async(request, pk: int):
    obj = CardSet.objects.get(pk=pk)
    if request.method == 'POST':
        form = CardSetForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            t_message = '<i class="fa fa-check"></i>'
        else:
            t_message = '<i class="fa fa-remove"></i> Error'
        context = {
            'card':
                {
                    'card': obj,
                    'count': Card.objects.filter(card_set_id=obj.id).count()
                },
            'success': True,
            't_message': t_message
        }
        return render(request, 'cards/cardset-list-tr-partial.html', context)
    context = {
        'form': CardSetForm(instance=obj),
        'obj': obj,
        'card_title': 'Update Card Set',
        'loaded': datetime.datetime.now()
    }
    return render(request, 'cards/cardset-form.html', context)


@login_required(login_url='/users/')
@error_handling
def card_set_form_refresh(request):
    context = {'card_title': 'Add Card Set', 'form': CardSetForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/cardset-form.html', context)


class CardListData:

    def __init__(self, qs: QuerySet):
        self.qs = qs

    def card_list_context(self, request) -> dict[str, str]:
        d_card_list = self.card_list_dict()
        request.session['rs'] = d_card_list
        return dict(
            rs=self.qs,
            loaded=timezone.now(),
            rs_dict=request.session['rs'] if 'rs' in request.session else []
        )

    def card_list_dict(self) -> list[dict[str, Any]]:
        return [
            {
                'player_name': c.player_id.player_fname + ' ' + c.player_id.player_lname,
                'year': c.card_set_id.year,
                'set_name': c.card_set_id.card_set_name,
                'info': c.card_subset,
                'num': c.card_num
            } for c in self.qs
        ]


def card_list_count(card_list: list) -> list[dict]:
    c_list = []
    for card in card_list:
        c_count = Card.objects.filter(card_set_id=card.id).count()
        if c_count > 0:
            c_list.append(dict(card=card, count=c_count))
    return c_list


class CardsListView(ListView):
    model = Card
    template_name = 'cards/card-list.html'
    context_object_name = 'cards'
    ordering = 'card_set_id__slug'
    paginate_by = 250

    def get_queryset(self):
        return Card.last_50.all()

    def get_context_data(self, **kwargs):
        data = super(CardsListView, self).get_context_data()
        data['title'] = f'Last {len(self.get_queryset())} Cards'
        data['form'] = CardCreateForm()
        data['card_title'] = 'Add New Card'
        c_data = CardListData(self.get_queryset())
        d_2 = c_data.card_list_context(self.request)
        return dict(data, **d_2)


class CardsViewAll(CardsListView):
    paginate_by = 250

    def get_queryset(self):
        return Card.list_all.all()

    def get_context_data(self, **kwargs):
        data = super(CardsViewAll, self).get_context_data()
        data['title'] = 'All Cards'
        data['form'] = CardCreateForm()
        data['card_title'] = 'Add New Card'
        c_list = CardListData(self.get_queryset())
        d_2 = c_list.card_list_context(self.request)
        return dict(data, **d_2)


class CardsViewSet(CardsListView):
    def get_object(self):
        return CardSet.objects.get(slug=self.kwargs.get('slug'))

    def get_card_set(self):
        card_set = self.get_object()
        return f'{card_set.year} {card_set.card_set_name}'

    def get_queryset(self):
        return Card.objects.filter(
            card_set_id__slug=self.kwargs.get('slug')
        ).order_by('card_num')

    def get_context_data(self, *, object_list=None, **kwargs):
        card_set = self.get_object()
        data = super(CardsViewSet, self).get_context_data(**kwargs)
        data['title'] = f'{self.get_card_set()}'
        data['card_set'] = card_set
        data['form'] = CardCreateForm(**{'set': card_set.slug})
        data['card_title'] = 'Add Card - Card Set'
        c_list = CardListData(self.get_queryset())
        d_2 = c_list.card_list_context(self.request)
        return dict(data, **d_2)


class CardsViewPlayer(CardsListView):
    def get_queryset(self):
        return Card.objects.filter(
            player_id__slug=self.kwargs.get('slug')
        ).order_by('card_set_id__year', 'card_set_id__slug')

    def get_object(self):
        return Player.objects.get(slug=self.kwargs.get('slug'))

    def get_player_name(self):
        player = self.get_object()
        return f'{player.player_fname} {player.player_lname}'

    def get_context_data(self, *, object_list=None, **kwargs):
        player = self.get_object()
        data = super(CardsViewPlayer, self).get_context_data(**kwargs)
        data['title'] = f'{self.get_player_name()}'
        data['player'] = player
        data['form'] = CardCreateForm(**{'player': player.slug})
        data['card_title'] = 'Add Card - Player'
        c_list = CardListData(self.get_queryset())
        d_2 = c_list.card_list_context(self.request)
        return dict(data, **d_2)


@error_handling
def card_list_pagination(request, cards: QuerySet):
    p = Paginator(cards, 100)
    page_number = request.GET['page'] if 'page' in request.GET else 1
    try:
        rs = p.get_page(page_number)
    except PageNotAnInteger:
        rs = p.page(1)
    except EmptyPage:
        rs = p.page(p.num_pages)
    return len(cards), rs, p.num_pages


# @login_required(login_url='/users/')
@error_handling
def card_list_last_n(request):
    cards = Card.last_50.all()
    card_count, rs, n_pages = card_list_pagination(request, cards)
    return render(
        request,
        'cards/card-list.html',
        {
            'title': f'Last {len(cards)} Cards',
            'rs': rs,
            'n_pages': n_pages,
            'card_count': card_count,
            'form': CardCreateForm,
            'card_title': 'Add Card'
        }
    )


# @login_required(login_url='/users/')
@error_handling
def card_list_by_player(request, slug: str):
    obj = Player.objects.get(slug=slug)
    cards = Card.objects.filter(
        player_id__slug=slug
    ).order_by('card_set_id__year', 'card_set_id__slug')
    card_count, rs, n_pages = card_list_pagination(request, cards)
    return render(
        request,
        'cards/card-list.html',
        {
            'title': f'{obj.player_fname} {obj.player_lname}',
            'rs': rs,
            'n_pages': n_pages,
            'card_count': card_count,
            'player': obj,
            'form': CardCreateForm(**{'player': obj.slug}),
            'card_title': 'Add Card - Player'
        }
    )


# @login_required(login_url='/users/')
@error_handling
def card_list_by_set(request, slug: str):
    obj = CardSet.objects.get(slug=slug)
    cards = Card.objects.filter(
        card_set_id__slug=slug
    ).order_by('card_num')
    card_count, rs, n_pages = card_list_pagination(request, cards)
    return render(
        request,
        'cards/card-list.html',
        {
            'title': f'{obj.year} {obj.card_set_name}',
            'rs': rs,
            'n_pages': n_pages,
            'card_count': card_count,
            'card_set': obj,
            'form': CardCreateForm(**{'set': obj.slug}),
            'card_title': 'Add Card - Cat Set'
        }
    )


# @login_required(login_url='/users/')
@error_handling
def card_list_all(request):
    cards = Card.objects.all().order_by('card_set_id__year', 'card_set_id__card_set_name', 'card_num')
    card_count, rs, n_pages = card_list_pagination(request, cards)
    return render(
        request,
        'cards/card-list.html',
        {
            'title': 'All Cards List',
            'rs': rs,
            'n_pages': n_pages,
            'card_count': card_count,
            'form': CardCreateForm,
            'card_title': 'Add Card'
        }
    )


@error_handling
def load_cards_async(request):
    card_count, rs, n_pages = card_list_pagination(request)
    context = {'rs': rs, 'loaded': timezone.now(), 'n_pages': n_pages, 'card_count': card_count}
    return render(request, 'cards/card-list-table-partial.html', context)


@login_required(login_url="/users/")
@error_handling
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
@error_handling
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
        'title': f'Last {len(cards)} Cards' if not player else f'{player.player_fname} {player.player_lname}'
    }
    return render(request, 'cards/card-list-card-partial.html', context)


@login_required(login_url='/users/')
@error_handling
def card_create_async(request, card_type: str = None, type_slug: str = None):
    new_id = None
    form = CardCreateForm(request.POST, request.FILES)
    if form.is_valid():
        player_id = form.cleaned_data['player_id']
        form.save()
        new_id = Card.objects.last().id
    if card_type and type_slug:
        if card_type == 'player':
            obj = Player.objects.get(slug=type_slug)
            cards = Card.objects.filter(player_id__slug=type_slug).order_by(
                'card_set_id__year', 'card_set_id__card_set_name')
            title = obj.player_fname + ' ' + obj.player_lname
        else:
            obj = CardSet.objects.get(slug=type_slug)
            cards = Card.objects.filter(card_set_id__slug=type_slug).order_by(
                'card_set_id__year', 'card_set_id__card_set_name')
            title = str(obj.year) + ' ' + obj.card_set_name
    else:
        cards = Card.last_50.all()
        title = f'Last {len(cards)} Cards'
    context = {
        'title': title,
        'new_id': new_id,
        'rs': cards,
    }
    return render(request, 'cards/card-list-card-partial.html', context)


@login_required(login_url='/users/')
@error_handling
def card_create_form_async(request, card_type: str = None, type_slug: str = None):
    form = CardCreateForm()
    context = {'card_title': 'Add Card'}
    if card_type and type_slug:
        if card_type == 'player':
            kwargs = {'player': type_slug}
            context['card_title'] = 'Add Card - Player'
        else:
            kwargs = {'set': type_slug}
            context['card_title'] = 'Add Card - Set'
        form = CardCreateForm(**kwargs)
    context['form'] = form
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
@error_handling
def card_form_refresh(request):
    context = {'card_title': 'Add New Card', 'form': CardCreateForm, 'loaded': datetime.datetime.now()}
    return render(request, 'cards/card-form.html', context)


@login_required(login_url='/users/')
@error_handling
def card_image(request, pk: int):
    obj = Card.objects.get(pk=pk)
    card_string = f'{obj.card_set_id.year} {obj.card_set_id.card_set_name} {obj.card_subset} {obj.card_num}'
    context = {'title': obj.card_image, 'object': obj, 'card_string': card_string}
    return render(request, 'cards/card-image.html', context)


def card_search_full_text(query: str) -> QuerySet:
    return Card.objects.search_query(query).order_by(
        'card_set_id__year',
        'card_set_id__card_set_name',
        'player_id__player_lname'
    )


@login_required(login_url='/users/')
@error_handling
def card_search(request):
    cards = []
    search = ''
    if request.method == 'POST':
        search = request.POST['search']
        cards = card_search_full_text(search)
        request.session['rs'] = CardListData(cards).card_list_dict()
    context = {
        'title': f'Search "{search}"',
        'form': CardCreateForm,
        'search': search,
        'card_title': 'Add New Card'
    }
    return render(
        request,
        'cards/card-list-card-partial.html',
        dict(context, **CardListData(cards).card_list_context(request))
    )


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

    def upload_excel(self) -> Any:
        wb = self.populate_excel_file()
        client = boto3.Session(os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY')).resource('s3')
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME')
        result = client.Bucket(bucket).upload_file(self.file_name, self.DEST_DIR + self.file_name)

        os.remove(self.file_name)

        print(result)
        return result


def export_list_save(request, file_name: str):
    export = CardListExport(user_id=request.user.id, file_name=file_name)
    export.save()


def card_list_export(rs: list[dict] | QuerySet) -> str:
    f_date = datetime.datetime.strftime(timezone.now(), '%m_%d_%Y__%H_%M_%S')
    file_name = f"bbcards_card_list_export_{str(f_date)}.xlsx"
    if len(rs) > 0:
        xl = ExportScriptsExcel(rs, file_name)
        xl.upload_excel()
    return file_name


def card_list_export_pdf(text: str = None) -> str:
    rs = card_search_full_text(text)
    html = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
    html += '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    html += '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">'

    html += '</head><body><div class="container"><h1>Test</h1><table>'
    for r in rs:
        html += '<tr>'
        html += f'<td>{r.player_id.player_fname} {r.player_id.player_lname}</td>'
        html += f'<td>{r.card_set_id.year}</td>'
        html += f'<td>{r.card_set_id.card_set_name}</td>'
        html += f'<td>{r.card_subset}</td>'
        html += f'<td>{r.card_num}</td>'
        html += '</tr>'
    html += f'</table><p>{len(rs)} records</p>'
    html += '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>'
    html += '</div></body></html>'
    return html


def html_to_pdf():
    pdf_path = 'test.pdf'
    html_content = card_list_export_pdf(None)
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    return not pisa_status.err


@login_required(login_url='/users/')
@csrf_exempt
# @error_handling
def card_list_export_vw_pdf(request, q: str = None):
    if request.method == 'POST':
        form = SearchForm(request.POST or None)
        if form.is_valid():
            search = form.cleaned_data['search']
        else:
            search = '<h1>Invalid input</h1>'
    else:
        search = 'Bo Jackson'
    return render(
        request,
        'cards/card-list-pdf-preview.html',
        {'output': card_list_export_pdf(search), 'pdf': html_to_pdf()}
    )


@login_required(login_url='/users/')
@csrf_exempt
@error_handling
def card_list_export_vw(request):
    rs = card_list_export(request.session['rs']) if 'rs' in request.session else ''
    if len(rs) > 0:
        export_list_save(request, rs)
    context = {
        'xport_result': rs,
        'xport_url': f'https://jojodave.s3.amazonaws.com/static/bbcards/export_data/{rs}'
    }
    return render(request, 'cards/card-list-export-msg-partial.html', context)
