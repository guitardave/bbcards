from django.urls import path, include

app_name = 'bbcards'

urlpatterns = [
    path('', include('cards.urls')),
    path('players/', include('players.urls')),
]
