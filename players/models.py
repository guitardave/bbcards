from django.db import models
from django.urls import reverse


class Player(models.Model):
    player_fname = models.CharField(max_length=50, default=None)
    player_lname = models.CharField(max_length=50, default=None)

    def __str__(self):
        return '%s %s' % (self.player_fname, self.player_lname)

    def get_absolute_url(self):
        return reverse('players:players-home')
