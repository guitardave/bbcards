from django.contrib.auth.models import User
from django.db import models
from players.models import Player


class CardUser(User):
    favorite_player = models.ForeignKey(Player, related_name='+', on_delete=models.CASCADE)
