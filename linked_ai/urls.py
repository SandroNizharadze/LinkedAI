from django.contrib import admin
from django.urls import path, include
from core.views.main import job_list, login_view, logout_view, register
from core.views.chatbot import chatbot

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', job_list, name='job_list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('chatbot/', chatbot, name='chatbot'),
    path('auth/', include('social_django.urls', namespace='social')),
]