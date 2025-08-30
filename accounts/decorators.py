from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Project, UserProfile


def superuser_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator para views que verifica se o usuário é superuser.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm):
    """
    Decorator para verificar se o usuário tem uma permissão específica
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(perm):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def can_edit_project(view_func):
    """
    Decorator para verificar se o usuário pode editar um projeto específico
    """

    @wraps(view_func)
    def _wrapped_view(request, project_id, *args, **kwargs):
        project = get_object_or_404(Project, id=project_id)

        # Superuser pode editar qualquer projeto
        if request.user.is_superuser:
            return view_func(request, project_id, *args, **kwargs)

        # Usuário normal só pode editar seus próprios projetos
        if project.user == request.user:
            return view_func(request, project_id, *args, **kwargs)

        raise PermissionDenied

    return _wrapped_view


def client_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator para views que requerem um usuário do tipo cliente
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.account_type == "CLIENT",
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def collaborator_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Decorator para views que requerem um usuário do tipo colaborador
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.account_type == "COLLABORATOR",
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
