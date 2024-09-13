from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify


class Player(models.Model):
    player_fname = models.CharField(max_length=50, default=None)
    player_lname = models.CharField(max_length=50, default=None)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return '%s %s' % (self.player_fname, self.player_lname)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.__str__())
        super(Player, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('players:players-home')
