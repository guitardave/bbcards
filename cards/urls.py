from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.card_list_last_n, name='card-list-50'),
    path('cards/', views.card_list_all, name='card-list-all'),
    path('cards/<int:sort_by>/', views.card_list_all, name='card-list-all'),
    path('cards/by-set/<slug:slug>/', views.card_list_by_set, name='card-list-set'),
    path('cards/by-player/<slug:slug>/', views.card_list_by_player, name='card-list-player'),
    path('cards/list/async/', views.load_cards_async, name='card-list-async'),
    path('cards/new/async/', views.card_create_async, name='card-new-async'),
    path('cards/new/async/<str:card_type>/<str:type_slug>/', views.card_create_async, name='card-new-async'),
    path('cards/new/form/async/', views.card_create_form_async, name='card-new-form-async'),
    path('cards/new/form/async/<str:card_type>/<str:type_slug>/', views.card_create_form_async, name='card-new-form-async'),
    path('cards/<slug:slug>/images/', views.card_image, name='card-image'),
    path('cards/<slug:slug>/update/async/', views.card_update_async, name='card-upd-async'),
    path('cards/<slug:slug>/delete/async/', views.card_delete_async, name='card-delete-async'),
    path('cards/form/refresh/async/', views.card_form_refresh, name='card-form-refresh'),
    path('sets/', views.card_set_list, name='cardsets'),
    path('sets/<int:n_count>/', views.card_set_list, name='cardsets'),
    path('sets/new/async/', views.card_set_create_async, name='cardsets-new-async'),
    path('sets/<slug:slug>/update/async/', views.card_set_update_async, name='cardsets-upd-async'),
    path('sets/<slug:slug>/delete/async/', views.card_set_delete_async, name='cardsets-delete-async'),
    path('sets/form/refresh/async/', views.card_set_form_refresh, name='cardsets-form-refresh'),
    path('search/', views.CardSearch.as_view(), name='search'),
    path('search/<str:search>/', views.card_search_pagination, name='search'),
    path('xport/async/', views.card_list_export_vw, name='cards-export'),
    path('xport/pdf/', views.card_list_export_vw_pdf, name='cards-export-pdf'),
    path('xport/pdf/<str:q>/', views.card_list_export_vw_pdf, name='cards-export-pdf'),
]
