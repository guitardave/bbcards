from django import forms

from players.models import Player
from .models import CardUser


class UserForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    favorite_player = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control form-control-lg'}),
        queryset=Player.objects.all()
    )

    class Meta:
        model = CardUser
        fields = ('email', 'username', 'first_name', 'last_name', 'favorite_player')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))
