from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cards_all, name='cards'),
    path('<int:card_id>/', views.get_card, name='card'),
    path('set/<int:card_set_id>/', views.get_cards_by_set, name='cards_by_set'),
    path('sets/', views.get_card_sets, name='sets'),
    path('sets/new/', views.create_card_set, name='create_set'),
    path('sets/<int:pk>/', views.update_card_set, name='update_set'),
    path('player/<int:player_id>/', views.get_cards_by_player, name='cards_by_player'),
    path('players/', views.get_players, name='players'),
    path('players/new/', views.create_player, name='create_player'),
    path('players/<int:player_id>/', views.update_player, name='update_player'),
]
