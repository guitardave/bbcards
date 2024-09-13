from django.urls import path, include

app_name = 'bbcards'

urlpatterns = [
    path('', include('cards.urls')),
    path('players/', include('players.urls')),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
]
