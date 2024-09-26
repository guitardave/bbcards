from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import *


SPORTS = [('Baseball', 'Baseball'), ('Football', 'Football'), ('Basketball', 'Basketball')]


def validate_int(value):
    if not int(value):
        raise ValidationError(
            _("%(value)s is not an integer"),
            params={'value': value}
        )


class CardCreateSetForm(forms.ModelForm):
    player_id = forms.ModelChoiceField(queryset=Player.objects.all().order_by('player_lname'))

    class Meta:
        model = Card
        fields = ('player_id', 'card_set_id', 'card_subset', 'card_num', 'card_image',)

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('slug')
        super(CardCreateSetForm, self).__init__(*args, **kwargs)
        self.fields['card_set_id'].queryset = CardSet.objects.filter(slug=qs)


class CardForm(forms.ModelForm):
    player_id = forms.ModelChoiceField(
        label='Player',
        queryset=Player.objects.all().order_by('player_lname'),
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'})
    )
    card_set_id = forms.ModelChoiceField(
        label='Card Set',
        queryset=CardSet.objects.all().order_by('year', 'card_set_name'),
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'})
    )
    card_subset = forms.CharField(
        label='Card Subset/Info',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    card_num = forms.CharField(
        label='Card number',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )

    class Meta:
        model = Card
        fields = ('player_id', 'card_set_id', 'card_subset', 'card_num', 'card_image',)


class CardCreateForm(CardForm):
    def __init__(self, *args, **kwargs):
        card_set = kwargs.pop('set') if 'set' in kwargs else None
        player = kwargs.pop('player') if 'player' in kwargs else None
        super(CardForm, self).__init__(*args, **kwargs)
        if card_set:
            self.fields['card_set_id'].initial = CardSet.objects.get(slug=card_set)
        if player:
            self.fields['player_id'].initial = Player.objects.get(slug=player)


class CardUpdateForm(CardForm):
    def __init__(self, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)
        self.fields['card_set_id'].queryset = CardSet.objects.all().order_by('card_set_name')


class CardSetForm(forms.ModelForm):
    year = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        label='Set Year',
        validators=[validate_int],
        required=True
    )
    card_set_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        label='Card Set Name',
        required=True
    )
    sport = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'}, choices=SPORTS),
        label='Sport',
    )

    class Meta:
        model = CardSet
        fields = ('year', 'card_set_name', 'sport',)


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50, help_text='Search by card set or description')
