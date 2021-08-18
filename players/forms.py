from django import forms
from .models import *

class PlayerForm(forms.Form):
	class Meta:
		model = Player
		fields = '__all__'