from django import forms
from .models import *

class CardForm(forms.ModelForm):
	class Meta:
		model = Card
		fields = "__all__"
        
        
class CardSetForm(forms.ModelForm):
    class Meta:
        model = CardSet
        fields = "__all__"