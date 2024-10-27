from datetime import datetime

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector, SearchQuery
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from players.models import Player
from users.models import CardUser


class CardSetAll(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all().order_by('year', 'card_set_name')


class CardSet(models.Model):
    LIMIT = settings.DEFAULT_LIMIT

    class Sports(models.TextChoices):
        BASEBALL = 'Baseball', _('Baseball')
        FOOTBALL = 'Football', _('Football')
        BASKETBALL = 'Basketball', _('Basketball')

    year = models.IntegerField(default=datetime.now().year)
    card_set_name = models.CharField(max_length=45, default=None)
    date_entered = models.DateTimeField(auto_now_add=True)
    sport = models.CharField(max_length=50, null=True, default=Sports.BASEBALL, choices=Sports.choices)
    slug = models.SlugField(unique=True)

    objects = models.Manager()
    all_sets = CardSetAll()
    
    def __str__(self):
        return '%s %s %s' % (str(self.year), self.card_set_name, self.sport)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.__str__())
        super(CardSet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cards:cardsets', kwargs={'n_count': self.LIMIT})


class CardSearchMgr(models.Manager):
    def search_query(self, raw_query: str):
        search_vector = SearchVector(
            'card_set_id__year',
            'card_set_id__card_set_name',
            'card_subset',
            'card_num',
            'player_id__player_fname',
            'player_id__player_lname',
            'card_set_id__sport'
        )
        search_query = SearchQuery(raw_query)
        return self.annotate(search=search_vector).filter(search=search_query)
        # return self.filter(search_vector=search_query)


class CardLast50Mgr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all().order_by('-id')[:25]


class CardsAllMgr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().all().order_by(
            'player_id__player_fname',
            'card_set_id__year',
            'card_set_id__card_set_name'
        )


class Card(models.Model):
    class Condition(models.TextChoices):
        MT = 'Mint', _('Mint')
        NM = 'Near Mint', _('Near Mint')
        EX = 'Excellent', _('Excellent')
        VG = 'Very Good', _('Very Good')
        G = 'Good', _('Good')
        F = 'Fair', _('Fair')

    slug = models.SlugField(null=True, max_length=250, unique=True)
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    card_num = models.CharField(max_length=50, default=None)
    card_set_id = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    card_subset = models.CharField(max_length=100, default=None, null=True, blank=True)
    card_image = models.FileField(upload_to='upload/', default=None, null=True, blank=True)
    date_entered = models.DateTimeField(auto_now_add=True)
    condition = models.CharField(max_length=100, default=None, null=True, blank=True, choices=Condition.choices)
    graded = models.BooleanField(default=False, null=True)
    search_vector = SearchVectorField(null=True)

    objects = CardSearchMgr()
    # objects = models.Manager()
    last_50 = CardLast50Mgr()
    list_all = CardsAllMgr()

    class Meta:
        indexes = (GinIndex(fields=['search_vector']),)

    def __str__(self):
        return f''' 
            {self.player_id.player_fname} {self.player_id.player_fname} 
            {self.card_set_id.year} 
            {self.card_set_id.card_set_name}
            {self.card_num}
        '''

    def save(self, *args, **kwargs):
        self.slug = slugify(
            f'{self.player_id.__str__()} {self.card_set_id.__str__()} {self.card_subset} {self.card_num}'
        )
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('cards:card-det', kwargs={'pk': self.id})


# @receiver(post_save, sender=Card)
# def update_search_vector(instance, sender, **kwargs):
#     inst = Card.objects.filter(id=instance.id).update(
#         search_vector=SearchVector(
#             'card_set_id__year',
#             'card_set_id__card_set_name',
#             'card_subset',
#             'card_num',
#             'player_id__player_fname',
#             'player_id__player_lname',
#             'card_set_id__sport'
#         )
#     )


class CardListExport(models.Model):
    user = models.ForeignKey(CardUser, on_delete=models.DO_NOTHING)
    file_name = models.CharField(max_length=200)
    date_entered = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.file_name
