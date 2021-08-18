from django.urls import path, include


app_name = 'bbcards'

urlpatterns = [

    path('cards/', include('cards.urls')),
    path('players/', include('players.urls')),
]
