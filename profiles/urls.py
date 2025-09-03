from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    # Profile views
    path("", views.ProfileView.as_view(), name="profile"),
    path(
        "public/<str:username>/",
        views.PublicProfileView.as_view(),
        name="public_profile",
    ),
    # AJAX endpoints
    path("ajax/upload-avatar/", views.upload_avatar, name="upload_avatar"),
    path("ajax/remove-avatar/", views.remove_avatar, name="remove_avatar"),
    path("ajax/get-profile-data/", views.get_profile_data, name="get_profile_data"),
]
