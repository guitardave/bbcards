from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.CardsListView.as_view(), name='card-list-all'),
    path('sets/', views.card_set_list, name='cardsets'),
    path('sets/new/', views.CardSetCreate.as_view(), name='cardsets-new'),
    path('sets/<int:pk>/update/async/', views.card_set_update_async, name='cardsets-upd-async'),
    path('cards/<slug:slug>/by-set/', views.CardsViewSet.as_view(), name='card-list-set'),
    path('cards/<slug:slug>/player/', views.CardsViewPlayer.as_view(), name='card-list-player'),
    path('cards/<slug:slug>/set/', views.CardList.as_view(), name='card-list'),
    path('cards/new/', views.CardCreate.as_view(), name='card-new-all'),
    path('cards/<slug:slug>/new/', views.CardNewSet.as_view(), name='card-new-set'),
    path('cards/<int:pk>/update/async/', views.card_update_async, name='card-upd-async'),
    path('sets/new/async/', views.card_set_create, name='cardsets-new-async'),
]
