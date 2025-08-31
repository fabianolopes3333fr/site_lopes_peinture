from django.shortcuts import render


def index(request):
    return render(request, "pages/index.html")


def nuancier(request):
    return render(request, "pages/nuancier.html")

def services(request):
    return render(request, "pages/services.html")

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    return render(request, "pages/contact.html")

def blog_list(request):
    return render(request, "pages/blog_list.html")
