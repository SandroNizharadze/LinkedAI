from django.urls import path
from .views.main import job_list, login_view, logout_view, register, profile
from .views.chatbot import chatbot

urlpatterns = [
    path('', job_list, name='job_list'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('chatbot/', chatbot, name='chatbot'),
    path('profile/', profile, name='profile'),
]