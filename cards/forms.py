from datetime import datetime
from django import forms
from .models import *


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
    player_id = forms.ModelChoiceField(label='Player', queryset=Player.objects.all().order_by('player_lname'))
    card_set_id = forms.ModelChoiceField(label='Card Set',
                                         queryset=CardSet.objects.all().order_by('year', 'card_set_name'))
    card_subset = forms.CharField(label='Card Subset/Info', required=False)
    card_num = forms.CharField(label='Card number')

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
    year = forms.IntegerField(max_value=datetime.now().year)

    class Meta:
        model = CardSet
        fields = ('year', 'card_set_name',)


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50, help_text='Search by card set or description')
