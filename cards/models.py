from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from players.models import Player


class CardSet(models.Model):
    year = models.IntegerField(default=datetime.now().year)
    card_set_name = models.CharField(max_length=45, default=None)
    date_entered = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return '%s %s' % (str(self.year), self.card_set_name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.__str__())
        super(CardSet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cards:cardsets')


class Card(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    card_num = models.CharField(max_length=50, default=None)
    card_set_id = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    card_subset = models.CharField(max_length=100, default=None, null=True, blank=True)
    card_image = models.FileField(upload_to='upload/', default=None, null=True, blank=True)
    date_entered = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.card_num
        
    def get_absolute_url(self):
        return reverse('cards:card-det', kwargs={'pk': self.id})
