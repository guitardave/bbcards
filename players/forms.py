from django import forms
from .models import *


class PlayerForm(forms.ModelForm):
	player_fname = forms.CharField(label='First Name')
	player_lname = forms.CharField(label='Last Name')

	class Meta:
		model = Player
		fields = ('player_fname', 'player_lname',)