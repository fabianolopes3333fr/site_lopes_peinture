from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .models import UserProfile
from .forms import (
    UserProfileForm,
)

from django.views.generic import UpdateView
from accounts.models import User
from accounts.decorators import (
    superuser_required,
    permission_required,
    can_edit_project,
)
from accounts.utils import generate_verification_token, export_user_data_to_csv

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
from django.utils.timezone import localtime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging


class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profiles:profile")

    def get_object(self):
        return self.request.user.profile


profile = ProfileView.as_view()


# AJAX Endpoints
@login_required
@require_POST
def upload_avatar(request):
    if "avatar" not in request.FILES:
        return JsonResponse({"error": "Aucune image n'a été fournie"}, status=400)

    profile = request.user.profile
    profile.avatar = request.FILES["avatar"]
    profile.save()

    return JsonResponse(
        {
            "status": "success",
            "message": "Avatar mis à jour avec succès",
            "avatar_url": profile.avatar.url,
        }
    )


@login_required
@require_POST
def remove_avatar(request):
    profile = request.user.profile
    profile.avatar = None
    profile.save()

    return JsonResponse({"status": "success", "message": "Avatar supprimé avec succès"})
