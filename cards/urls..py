from django.urls import path

from . import views

app_name = 'cards'

urlpatterns = [
	path('', views.home, 'card-home'),
    path('cards/<id>/', CardsView.as_view(), name='card-list')
]