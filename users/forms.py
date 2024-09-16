from django import forms
from .models import CardUser


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))

    class Meta:
        model = CardUser
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'favorite_player')


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}))
