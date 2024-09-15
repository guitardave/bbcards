from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.CardsListView.as_view(), name='card-list-50'),
    path('cards/', views.CardsViewAll.as_view(), name='card-list-all'),
    path('cards/by-set/<slug:slug>/', views.CardsViewSet.as_view(), name='card-list-set'),
    path('cards/by-player/<slug:slug>/', views.CardsViewPlayer.as_view(), name='card-list-player'),
    path('cards/new/async/', views.card_create_async, name='card-new-async'),
    path('cards/<int:pk>/update/async/', views.card_update_async, name='card-upd-async'),
    path('cards/form/refresh/async/', views.card_form_refresh, name='card-form-refresh'),
    path('sets/', views.card_set_list, name='cardsets'),
    path('sets/new/async/', views.card_set_create_async, name='cardsets-new-async'),
    path('sets/<int:pk>/update/async/', views.card_set_update_async, name='cardsets-upd-async'),
    path('sets/form/refresh/async/', views.card_set_form_refresh, name='cardsets-form-refresh'),
]

