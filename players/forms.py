from django import forms
from .models import *


class PlayerForm(forms.ModelForm):
	player_fname = forms.CharField(
		label='First Name',
		widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
	)
	player_lname = forms.CharField(
		label='Last Name',
		widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
	)

	class Meta:
		model = Player
		fields = ('player_fname', 'player_lname',)
