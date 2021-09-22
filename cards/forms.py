from django import forms
from .models import *


class CardCreateForm(forms.ModelForm):
    card_set_id = forms.ModelChoiceField(queryset=CardSet.objects.all().order_by('slug'))
    player_id = forms.ModelChoiceField(queryset=Player.objects.all().order_by('player_lname'))

    class Meta:
        model = Card
        fields = "__all__"


class CardUpdateForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('pk')
        super(CardUpdateForm, self).__init__(*args, **kwargs)
        self.fields['card_set_id'].queryset = CardSet.objects.all().order_by('card_set_name')


class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = "__all__"


class SearchForm(forms.Form):
    search = forms.CharField(max_length=50, help_text='Search by card set or description')