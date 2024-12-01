from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import *

YN = [('False', _('No')), ('True', _('Yes'))]


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


class DefaultChoice:
    @staticmethod
    def choices():
        return [(0, 'Select One')]


class CardForm(forms.ModelForm):
    class PlayerList:
        @staticmethod
        def choices():
            default_choice = DefaultChoice.choices()
            return default_choice + [
                (x.id, f'{x.__str__()}') for x in Player.objects.all().order_by('player_lname')
            ]

    class CardSetsList:
        @staticmethod
        def choices():
            default_choice = DefaultChoice.choices()
            return default_choice + [
                (x.id, f'{x.__str__()}') for x in CardSet.objects.all().order_by('year', 'card_set_name')
            ]

    player_id = forms.ModelChoiceField(
        queryset=Player.objects.all().order_by('player_lname'),
        label='',
        empty_label='Player',
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Player'})
    )
    # player_id = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={'class': 'form-control', 'placeholder': 'Player'}
    #     ),
    #     label=''
    # )

    card_set_id = forms.ModelChoiceField(
        queryset=CardSet.objects.all().order_by('year', 'card_set_name'),
        label='',
        empty_label='Card Set',
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Card Set'})
    )
    # card_set_id = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={'class': 'form-control', 'placeholder': 'Card Set'}
    #     ),
    #     label=''
    # )

    card_subset = forms.CharField(
        label='',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subset/Info'})
    )
    card_num = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card #'}),
        required=True
    )
    graded = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-control'}, choices=YN),
        label='Graded?',
        required=True
    )
    condition = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-control'}, choices=Card.Condition.choices),
        label='Card condition (estimate if raw)',
        required=True
    )

    class Meta:
        model = Card
        fields = ('player_id', 'card_set_id', 'card_subset', 'card_num', 'card_image', 'graded', 'condition')


class CardCreateForm(CardForm):
    def __init__(self, *args, **kwargs):
        card_set = kwargs.pop('set') if 'set' in kwargs else None
        player = kwargs.pop('player') if 'player' in kwargs else None
        super(CardForm, self).__init__(*args, **kwargs)
        if card_set:
            x = CardSet.objects.get(slug=card_set)
            # self.fields['card_set_id'].initial = (x.id, x.__str__())
            self.fields['card_set_id'].initial = x
        if player:
            x = Player.objects.get(slug=player)
            # self.fields['player_id'].initial = (x.id, x.__str__())
            self.fields['player_id'].initial = x


class CardUpdateForm(CardForm):
    def __init__(self, *args, **kwargs):
        super(CardForm, self).__init__(*args, **kwargs)
        self.fields['card_set_id'].queryset = CardSet.objects.all().order_by('card_set_name')


class CardSetForm(forms.ModelForm):
    year = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
        label='',
        validators=[validate_int],
        required=True
    )
    card_set_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Set Name'}),
        label='',
        required=True
    )
    sport = forms.CharField(
        widget=forms.Select(
            attrs={'class': 'form-control', 'placeholder': 'Sport'},
            choices=CardSet.Sports.choices
        ),
        label='',
    )

    class Meta:
        model = CardSet
        fields = ('year', 'card_set_name', 'sport',)


class SearchForm(forms.Form):
    search = forms.CharField(
        widget=forms.TextInput,
        max_length=50,
        help_text='Search by card set or description'
    )
