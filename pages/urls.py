from django.urls import path
from pages import views

app_name = "pages"

urlpatterns = [
    path("", views.index, name="home"),
    path("nuancier/", views.nuancier, name="nuancier"),
    path("services/", views.services, name="services"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("blog/", views.blog_list, name="blog_list"),
]
