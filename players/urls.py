from django.urls import path
from . import views

app_name = 'players'

urlpatterns = [
	path('', views.home, 'players-home'),
	path('<int:pk>/', views.CardsetList.as_view(), name='players-det'),
	path('new/', views.CardSetCreate.as_view(), name='players-new'),
    path('<int:pk>/update/', views.CardSetCreate.as_view(), name='players-upd'),
    
]