from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "profiles"

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('ajax/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('ajax/remove-avatar/', views.remove_avatar, name='remove_avatar'),
   
]
