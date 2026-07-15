from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from cards.models import Card, CardSet
from players.models import Player


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for player objects"""
    class Meta:
        model = Player
        fields = ['id', 'player_fname', 'player_lname']
        read_only_fields = ['id']


class CardSerializer(serializers.ModelSerializer):
    """Serializer for card objects"""
    player_id = serializers.StringRelatedField(read_only=True)
    card_set_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Card
        fields = ('id', 'player_id', 'card_set_id', 'card_subset', 'card_num', 'graded', 'condition')
        read_only_fields = ['id']


class CardSetSerializer(serializers.ModelSerializer):
    """Serializer for cardset objects"""
    class Meta:
        model = CardSet
        fields = ['id', 'year', 'card_set_name', 'sport']
