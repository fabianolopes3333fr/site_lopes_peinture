from django.urls import path
from config import views

app_name = "config"

urlpatterns = [
    path("", views.painel_view, name="painel"),
    # Settings URLs
    path("settings/", views.settings_view, name="settings"),
    path("settings/profile/update/", views.update_profile, name="update_profile"),
    path(
        "settings/notifications/update/",
        views.update_notifications,
        name="update_notifications",
    ),
    path("settings/password/change/", views.change_password, name="change_password"),
    path("settings/data/export/", views.export_data, name="export_data"),
    path("settings/account/delete/", views.delete_account, name="delete_account"),
    path("settings/login-history/", views.login_history, name="login_history"),
]
