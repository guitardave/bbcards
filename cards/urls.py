from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.home, name='home'),
    path('sets/', views.CardSetList.as_view(), name='cardsets'),
    path('sets/new/', views.CardSetCreate.as_view(), name='cardsets-new'),
    path('sets/<int:pk>/update/', views.CardSetUpdate.as_view(), name='cardsets-upd'),  # not linked yet 9/21
    path('cards/search', views.card_search, name='card-search'),
    path('cards/<id>/player/', views.CardsViewPLayer.as_view(), name='card-list-player'),
    path('cards/<id>/set/', views.CardsView.as_view(), name='card-list'),
    path('cards/all/', views.CardsView.as_view(), name='card-list-all'),
    path('cards/new/', views.CardCreate.as_view(), name='card-new-all'),
    path('cards/<int:pk>/', views.CardsDetail.as_view(), name='card-det'),
    path('cards/<int:pk>/update/', views.CardUpdate.as_view(), name='card-upd'),  # not linked yet 9/21
]