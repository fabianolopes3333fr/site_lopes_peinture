from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
)
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from .models import Project
from accounts.models import User
from accounts.decorators import can_edit_project
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
from django.utils.timezone import localtime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging
from .forms import ProjectForm
logger = logging.getLogger(__name__)


# Projetos
@method_decorator(login_required, name="dispatch")
class ProjectListView(ListView):
    template_name = "projects/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


mes_projets = ProjectListView.as_view()


@method_decorator(login_required, name="dispatch")
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:mes_projets")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


criar_projeto = ProjectCreateView.as_view()


@login_required
def projeto_detail(request, projeto_id):
    """
    View para exibir os detalhes de um projeto específico.
    Apenas o proprietário do projeto ou um administrador pode visualizar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    # Verifica se o usuário tem permissão para ver o projeto
    if not (request.user.is_superuser or projeto.user == request.user):
        messages.error(request, "Vous n'avez pas l'autorisation de voir ce projet.")
        return redirect("accounts:mes_projets")

    context = {
        "projeto": projeto,
        "can_edit": request.user.is_superuser or projeto.user == request.user,
        "title": f"Projet: {projeto.type_projet}",
    }

    return render(request, "projects/projeto_detail.html", context)


@login_required
@can_edit_project
def editar_projeto(request, projeto_id):
    """
    View para editar um projeto existente.
    Apenas o proprietário do projeto ou um administrador pode editar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, "Projet mis à jour avec succès!")
            return redirect("projects:projeto_detail", projeto_id=projeto.id)
    else:
        form = ProjectForm(instance=projeto)

    context = {
        "form": form,
        "projeto": projeto,
        "title": "Modifier le projet",
        "button_text": "Enregistrer les modifications",
    }

    return render(request, "projects/edit_projeto.html", context)


@login_required
@can_edit_project
def deletar_projeto(request, projeto_id):
    """
    View para deletar um projeto existente.
    Apenas o proprietário do projeto ou um administrador pode deletar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    if request.method == "POST":
        projeto.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect("projects:mes_projets")

    return render(
        request,
        "projects/delete_projeto.html",
        {"projeto": projeto, "title": "Supprimer le projet"},
    )
