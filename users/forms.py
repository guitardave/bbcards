from django import forms
from .models import CardUser


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CardUser
        fields = ('email', 'username', 'password', 'first_name', 'last_name', 'favorite_player')
