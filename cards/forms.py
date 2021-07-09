from django import forms
from .models import *

class CardForm(models.ModelForm):
	class Meta:
		model = Card
		fields = "__all__"
        
        
class CardSetForm(models.ModelForm):
    class Meta:
        model = CardSet
        fields = "__all__"