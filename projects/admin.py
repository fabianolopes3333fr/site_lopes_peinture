from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administração avançada para projetos."""

    list_display = [
        "title",
        "user_email",
        "type_projet",
        "status_colored",
        "priority_colored",
        "ville",
        "budget_estime",
        "created_at",
    ]
    list_filter = [
        "status",
        "type_projet",
        "priority",
        "created_at",
        "date_debut_souhaitee",
        "ville",
        "pays",
    ]
    search_fields = [
        "title",
        "user__email",
        "user__first_name",
        "user__last_name",
        "description",
        "ville",
        "adresse_travaux",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            _("Informations générales"),
            {"fields": ("title", "user", "type_projet", "description")},
        ),
        (_("Détails techniques"), {"fields": ("surface", "nombre_pieces")}),
        (
            _("Planning"),
            {
                "fields": (
                    "date_debut_souhaitee",
                    "date_fin_souhaitee",
                    "date_debut_effective",
                    "date_fin_effective",
                )
            },
        ),
        (_("Statut et priorité"), {"fields": ("status", "priority")}),
        (
            _("Localisation"),
            {
                "fields": (
                    "adresse_travaux",
                    "complement_adresse",
                    "code_postal",
                    "ville",
                    "pays",
                )
            },
        ),
        (_("Informations financières"), {"fields": ("budget_estime", "devis_montant")}),
        (
            _("Notes"),
            {"fields": ("notes_client", "notes_internes"), "classes": ("collapse",)},
        ),
        (
            _("Métadonnées"),
            {
                "fields": ("created_at", "updated_at", "completed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["created_at", "updated_at", "completed_at"]

    def user_email(self, obj):
        """Retorna o email do usuário."""
        return obj.user.email

    user_email.short_description = _("Client")
    user_email.admin_order_field = "user__email"

    def status_colored(self, obj):
        """Exibe o status com cores."""
        colors = {
            "brouillon": "#6B7280",
            "en_reflexion": "#3B82F6",
            "devis_demande": "#F59E0B",
            "devis_recu": "#8B5CF6",
            "devis_approuve": "#10B981",
            "planifie": "#06B6D4",
            "en_cours": "#059669",
            "termine": "#22C55E",
            "annule": "#EF4444",
            "en_attente": "#F97316",
        }

        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = _("Statut")
    status_colored.admin_order_field = "status"

    def priority_colored(self, obj):
        """Exibe a prioridade com cores."""
        colors = {
            "faible": "#10B981",
            "normale": "#3B82F6",
            "elevee": "#F59E0B",
            "urgente": "#EF4444",
        }

        color = colors.get(obj.priority, "#3B82F6")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display(),
        )

    priority_colored.short_description = _("Priorité")
    priority_colored.admin_order_field = "priority"

    def get_queryset(self, request):
        """Otimiza queries."""
        return super().get_queryset(request).select_related("user")

    def changelist_view(self, request, extra_context=None):
        """Adiciona estatísticas à view de lista."""
        extra_context = extra_context or {}

        # Estatísticas
        queryset = self.get_queryset(request)
        extra_context["stats"] = {
            "total": queryset.count(),
            "active": queryset.filter(
                status__in=["en_cours", "planifie", "devis_approuve"]
            ).count(),
            "completed": queryset.filter(status="termine").count(),
            "urgent": queryset.filter(priority="urgente").count(),
        }

        return super().changelist_view(request, extra_context)

    actions = ["mark_completed", "mark_cancelled", "export_projects"]

    def mark_completed(self, request, queryset):
        """Marca projetos como concluídos."""
        updated = queryset.update(status=Project.Status.COMPLETED)
        self.message_user(
            request,
            _("{count} projet(s) marqué(s) comme terminé(s).").format(count=updated),
        )

    mark_completed.short_description = _("Marquer comme terminé")

    def mark_cancelled(self, request, queryset):
        """Marca projetos como cancelados."""
        updated = queryset.update(status=Project.Status.CANCELLED)
        self.message_user(
            request,
            _("{count} projet(s) marqué(s) comme annulé(s).").format(count=updated),
        )

    mark_cancelled.short_description = _("Marquer comme annulé")
