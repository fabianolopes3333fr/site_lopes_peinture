from django.shortcuts import render, redirect
from django.contrib import messages





def nuancier(request):
    return render(request, "pages/nuancier.html")


def services(request):
    return render(request, "pages/services.html")


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    return render(request, "pages/contact.html")


def portfolio(request):
    return render(request, "pages/portfolio.html")


def terms(request):
    return render(request, "pages/terms.html")

def privacy(request):
    return render(request, "pages/privacy.html")

def blog_list(request):
    return render(request, "pages/blog_list.html")


# ... suas views existentes ...


def redirect_to_accounts_login(request):
    """Redirect amigável para login"""
    return redirect("accounts:login")


def redirect_to_accounts_register(request):
    """Redirect amigável para registro"""
    return redirect("accounts:register")


def home(request):
    """Home page com links para autenticação"""
    context = {
        "user": request.user if request.user.is_authenticated else None,
    }
    return render(request, "pages/index.html", context)


# ... resto das suas views existentes ...
