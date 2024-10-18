from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from cards.models import Card, CardSet
from players.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    player_id = serializers.StringRelatedField(read_only=True)
    card_set_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Card
        fields = ('id', 'player_id', 'card_set_id', 'card_subset', 'card_num', 'graded', 'condition')


class CardSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardSet
        fields = '__all__'
