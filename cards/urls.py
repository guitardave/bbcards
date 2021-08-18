from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
	path('', views.home, 'card-home'),
	path('sets/', views.CardsetList.as_view(), name='cardsets'),
	path('sets/new/', views.CardSetCreate.as_view(), name='cardsets-new'),
    path('cards/<id>/', views.CardsView.as_view(), name='card-list'),
    path('cards/<id>/new/', views.CardCreate.as_view(), name='card-new'),
    path('cards/new/', views.CardCreate.as_view(), name='card-new-all'),
    path('cards/<int:pk>/', views.CardsDetail.as_view(), name='card-det'),
]