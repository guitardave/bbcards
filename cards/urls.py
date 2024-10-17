from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.CardsListView.as_view(), name='card-list-50'),
    path('cards/', views.CardsViewAll.as_view(), name='card-list-all'),
    path('cards/by-set/<slug:slug>/', views.CardsViewSet.as_view(), name='card-list-set'),
    path('cards/by-player/<slug:slug>/', views.CardsViewPlayer.as_view(), name='card-list-player'),
    path('cards/list/async/<str:c_type>/<str:t_slug>/<int:page>/', views.load_cards_async, name='card-list-async'),
    path('cards/new/async/', views.card_create_async, name='card-new-async'),
    path('cards/new/async/<str:card_type>/<str:type_slug>/', views.card_create_async, name='card-new-async'),
    path('cards/new/form/async/', views.card_create_form_async, name='card-new-form-async'),
    path('cards/new/form/async/<str:card_type>/<str:type_slug>/', views.card_create_form_async, name='card-new-form-async'),
    path('cards/<int:pk>/images/', views.card_image, name='card-image'),
    path('cards/<int:pk>/update/async/', views.card_update_async, name='card-upd-async'),
    path('cards/<int:pk>/delete/async/', views.card_delete_async, name='card-delete-async'),
    path('cards/form/refresh/async/', views.card_form_refresh, name='card-form-refresh'),
    path('sets/', views.card_set_list, name='cardsets'),
    path('sets/<int:page_num>/', views.card_set_load_more, name='cardsets-load-more'),
    path('sets/new/async/', views.card_set_create_async, name='cardsets-new-async'),
    path('sets/<int:pk>/update/async/', views.card_set_update_async, name='cardsets-upd-async'),
    path('sets/form/refresh/async/', views.card_set_form_refresh, name='cardsets-form-refresh'),
    path('search/', views.card_search, name='search'),
    path('xport/async/', views.card_list_export_vw, name='cards-export'),
    path('xport/pdf/', views.card_list_export_vw_pdf, name='cards-export-pdf'),
]
