from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    # ==================== PÁGINAS PRINCIPAIS ====================
    # Home page
    path("", views.home, name="home"),
    
    # Sobre nós
    path("about/", views.about, name="about"),
    path("a-propos/", views.about, name="about_fr"),
    
    # Serviços
    path("services/", views.services, name="services"),
    path("nos-services/", views.services, name="services_fr"),
    
    # Contato
    path("contact/", views.contact, name="contact"),
    
    # Portfolio/Galeria
    path("portfolio/", views.portfolio, name="portfolio"),
    path("galerie/", views.portfolio, name="portfolio_fr"),
    
    # ==================== PÁGINAS DE APOIO ====================
    # Política de privacidade
    path("privacy/", views.privacy, name="privacy"),
    path("confidentialite/", views.privacy, name="privacy_fr"),
    
    # Termos de uso
    path("terms/", views.terms, name="terms"),
    path("conditions/", views.terms, name="terms_fr"),
    
    # ==================== REDIRECTS PARA LOGIN ====================
    # URLs amigáveis que redirecionam para login/registro
    path("login/", views.redirect_to_accounts_login, name="login_redirect"),
    path("register/", views.redirect_to_accounts_register, name="register_redirect"),
    path("connexion/", views.redirect_to_accounts_login, name="login_redirect_fr"),
    path("inscription/", views.redirect_to_accounts_register, name="register_redirect_fr"),

    path("nuancier/", views.nuancier, name="nuancier"),
    path("blog_list/", views.blog_list, name="blog_list"),
    
    
]