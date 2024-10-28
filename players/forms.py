from django import forms
from .models import *


class PlayerForm(forms.ModelForm):
	player_fname = forms.CharField(
		label='',
		widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
	)
	player_lname = forms.CharField(
		label='',
		widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
	)

	class Meta:
		model = Player
		fields = ('player_fname', 'player_lname',)
