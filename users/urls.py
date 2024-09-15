from django.urls import path
from django.contrib.auth import login, logout
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:pk>/update', views.UserUpdate.as_view(), name='user-update'),
    path('<int:pk>/profile', views.UserDetail.as_view(), name='user-profile'),
]
