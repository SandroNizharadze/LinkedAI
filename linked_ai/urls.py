from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include core.urls to use its URL patterns
    path('auth/', include('social_django.urls', namespace='social')),
]