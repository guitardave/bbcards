from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
	path('', views.player_list, name='players-home'),
	path('new/', views.player_add_async, name='players-new'),
	path('<int:pk>/update/async/', views.player_update_async, name='players-upd-async'),
	path('form/refresh/async/', views.player_form_refresh, name='players-form-refresh'),
]
