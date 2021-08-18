from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
	path('', views.PlayerList.as_view(), 'players-home'),
	path('<int:pk>/', views.PlayerDetail.as_view(), name='players-det'),
	path('new/', views.PlayerNew.as_view(), name='players-new'),
    path('<int:pk>/update/', views.PlayerUpdate.as_view(), name='players-upd'),
    
]