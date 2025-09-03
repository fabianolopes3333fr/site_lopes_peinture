from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Administração do modelo UserProfile."""

    list_display = [
        "user_email",
        "user_full_name",
        "phone",
        "has_avatar",
        "age_display",
        "created_at",
    ]
    list_filter = ["created_at", "updated_at", "date_of_birth"]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "phone",
        "address",
    ]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at", "updated_at", "age_display", "avatar_preview"]

    fieldsets = (
        (None, {"fields": ("user", "avatar_preview", "avatar")}),
        (_("Informations de contact"), {"fields": ("phone", "address")}),
        (
            _("Informations personnelles"),
            {"fields": ("bio", "date_of_birth", "age_display")},
        ),
        (
            _("Métadonnées"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def user_email(self, obj):
        """Retorna o email do usuário."""
        return obj.user.email

    user_email.short_description = _("Email")
    user_email.admin_order_field = "user__email"

    def user_full_name(self, obj):
        """Retorna o nome completo do usuário."""
        return obj.user.get_full_name()

    user_full_name.short_description = _("Nom complet")
    user_full_name.admin_order_field = "user__first_name"

    def has_avatar(self, obj):
        """Indica se o usuário tem avatar."""
        if obj.avatar:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')

    has_avatar.short_description = _("Avatar")
    has_avatar.boolean = True

    def age_display(self, obj):
        """Exibe a idade do usuário."""
        return f"{obj.age} ans" if obj.age else "-"

    age_display.short_description = _("Âge")

    def avatar_preview(self, obj):
        """Preview do avatar no admin."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return _("Aucun avatar")

    avatar_preview.short_description = _("Aperçu de l'avatar")

    def get_queryset(self, request):
        """Otimiza as queries."""
        return super().get_queryset(request).select_related("user")
