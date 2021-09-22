from django.urls import path
from django.contrib.auth import login, logout
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('weather/', views.weather, name='weather'),
]