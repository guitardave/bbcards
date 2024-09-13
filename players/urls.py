from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
	path('', views.PlayerList.as_view(), name='players-home'),
	path('<slug:slug>/detail/', views.PlayerDetail.as_view(), name='players-det'),
	path('new/', views.player_add, name='players-new'),
	path('<slug:slug>/update/', views.PlayerUpdate.as_view(), name='players-upd'),
]