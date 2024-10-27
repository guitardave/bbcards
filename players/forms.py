from django import forms
from .models import *


class PlayerForm(forms.ModelForm):
	player_fname = forms.CharField(
		label='First Name',
		widget=forms.TextInput(attrs={'class': 'form-control'})
	)
	player_lname = forms.CharField(
		label='Last Name',
		widget=forms.TextInput(attrs={'class': 'form-control'})
	)

	class Meta:
		model = Player
		fields = ('player_fname', 'player_lname',)
