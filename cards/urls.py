from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.CardsListView.as_view(), name='card-list-all'),
    path('sets/', views.card_set_list, name='cardsets'),
    path('sets/new/', views.CardSetCreate.as_view(), name='cardsets-new'),
    path('sets/<slug:slug>/update/', views.CardSetUpdate.as_view(), name='cardsets-upd'),
    path('cards/<slug:slug>/by-set/', views.CardsView.as_view(), name='card-list-set'),
    path('cards/<slug:slug>/player/', views.CardsViewPlayer.as_view(), name='card-list-player'),
    path('cards/<slug:slug>/set/', views.CardList.as_view(), name='card-list'),
    path('cards/new/', views.CardCreate.as_view(), name='card-new-all'),
    path('cards/<slug:slug>/new/', views.CardNewSet.as_view(), name='card-new-set'),
    path('cards/<int:pk>/', views.CardsDetail.as_view(), name='card-det'),
    path('cards/<int:pk>/update/', views.CardUpdate.as_view(), name='card-upd'),
]