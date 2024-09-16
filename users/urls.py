from django.urls import path
from django.contrib.auth import login, logout
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:pk>/update/', views.UserUpdate.as_view(), name='user-update'),
    path('<int:pk>/password/', views.password_update, name='user-update-password'),
    path('<int:pk>/profile/', views.UserDetail.as_view(), name='user-profile'),
    path('management/', views.user_management_list, name='user-management'),
    path('management/<int:pk>/update/', views.user_management_update, name='user-management-upd'),
    path('toggle_mode/', views.toggle_view_mode, name='toggle_mode'),
    path('toggle_mode/<str:mode>/', views.toggle_view_mode, name='toggle_mode'),
]
