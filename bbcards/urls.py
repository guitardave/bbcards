from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = 'bbcards'

urlpatterns = [
    path('', include('cards.urls')),
    path('players/', include('players.urls')),
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
