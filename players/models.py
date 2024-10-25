from django.db import models
from django.urls import reverse
from django.template.defaultfilters import slugify


class PlayerListMgr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all().order_by('player_lname')


class PlayerListNoIgnore(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(ignore=False).order_by('player_lname')


class PlayerListIgnore(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(ignore=True).order_by('player_lname')


class Player(models.Model):
    player_fname = models.CharField(max_length=50, default=None)
    player_lname = models.CharField(max_length=50, default=None)
    slug = models.SlugField(unique=True)
    ignore = models.BooleanField(default=False)

    objects = models.Manager()
    list_all = PlayerListMgr()
    list_ignore = PlayerListIgnore()
    list_no_ignore = PlayerListNoIgnore()

    def __str__(self):
        return '%s %s' % (self.player_fname, self.player_lname)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.__str__())
        super(Player, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('players:players-home')
