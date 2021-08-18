from django.db import models
from django.urls import reverse
from players.models import Player


class CardSet(models.Model):
    year = models.SmallIntegerField(default=0)
    card_set_name = models.CharField(max_length=100, default=None)
    date_entered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s %s' % (str(self.year), self.card_set)
        
    def get_absolute_url(self):
        return reverse('cards:cardset-home')


class Card(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    card_num = models.CharField(max_length=50, default=None)
    card_set_id = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    card_subset = models.CharField(max_length=100, default=None, null=True)
    date_entered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.card_num
        
    def get_absolute_url(self):
        return reverse('cards:card-list', kwargs={'id': self.card_set_id})
        
 
