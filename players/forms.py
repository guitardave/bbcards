from django import forms
from .models import *

class PlayerForm(forms.ModelForm):
	class Meta:
		model = Player
		fields = '__all__'