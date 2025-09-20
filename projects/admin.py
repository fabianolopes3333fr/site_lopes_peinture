from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count
from .models import Project, Product, Devis, DevisLine, DevisHistory


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Administração avançada para projetos."""

    list_display = [
        "reference",
        "title",
        "user_email",
        "project_type",
        "status_colored",
        "priority_colored",
        "ville",
        "budget_display",
        "created_at",
    ]
    list_filter = [
        "status",
        "project_type",
        "priority",
        "created_at",
        "date_debut_souhaitee",
        "ville",
        "pays",
        "etat_support",
        "type_finition",
    ]
    search_fields = [
        "reference",
        "title",
        "user__email",
        "user__first_name",
        "user__last_name",
        "description",
        "ville",
        "adresse_travaux",
        "notes_client",
        "notes_internes",
    ]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            _("Informations générales"),
            {
                "fields": (
                    "reference",
                    "title",
                    "user",
                    "assigned_to",
                    "project_type",
                    "description",
                    "priority",
                    "status",
                )
            },
        ),
        (
            _("Détails techniques"),
            {
                "fields": (
                    "surface_totale",
                    "surface_murs",
                    "surface_plafond",
                    "hauteur_sous_plafond",
                    "nombre_pieces",
                    "types_pieces",
                    "etat_support",
                    "preparation_necessaire",
                    "type_finition",
                    "couleurs_souhaitees",
                    "materiaux_specifiques",
                    "acces_difficile",
                    "contraintes_horaires",
                )
            },
        ),
        (
            _("Planning"),
            {
                "fields": (
                    "date_debut_souhaitee",
                    "date_fin_souhaitee",
                    "date_debut_prevue",
                    "date_fin_prevue",
                    "date_debut_effective",
                    "date_fin_effective",
                )
            },
        ),
        (
            _("Localisation"),
            {
                "fields": (
                    "adresse_travaux",
                    "complement_adresse",
                    "code_postal",
                    "ville",
                    "pays",
                    "contact_nom",
                    "contact_telephone",
                )
            },
        ),
        (
            _("Informations financières"),
            {"fields": ("budget_minimum", "budget_maximum")},
        ),
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

    readonly_fields = ["reference", "created_at", "updated_at", "completed_at"]

    def budget_display(self, obj):
        """Exibe o orçamento formatado"""
        if obj.budget_minimum and obj.budget_maximum:
            return f"{obj.budget_minimum}€ - {obj.budget_maximum}€"
        elif obj.budget_maximum:
            return f"Jusqu'à {obj.budget_maximum}€"
        elif obj.budget_minimum:
            return f"À partir de {obj.budget_minimum}€"
        return "-"

    budget_display.short_description = _("Budget")
    budget_display.admin_order_field = "budget_maximum"

    def user_email(self, obj):
        """Retorna o email do usuário."""
        return obj.user.email

    user_email.short_description = _("Client")
    user_email.admin_order_field = "user__email"

    def status_colored(self, obj):
        """Exibe o status com cores."""
        colors = {
            "brouillon": "#6B7280",
            "soumis": "#3B82F6",
            "en_examen": "#8B5CF6",
            "devis_demande": "#F59E0B",
            "devis_envoye": "#8B5CF6",
            "devis_accepte": "#10B981",
            "devis_refuse": "#EF4444",
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
        return super().get_queryset(request).select_related("user", "assigned_to")

    def changelist_view(self, request, extra_context=None):
        """Adiciona estatísticas à view de lista."""
        extra_context = extra_context or {}

        # Estatísticas
        queryset = self.get_queryset(request)
        extra_context["stats"] = {
            "total": queryset.count(),
            "active": queryset.filter(
                status__in=["en_cours", "planifie", "devis_accepte"]
            ).count(),
            "completed": queryset.filter(status="termine").count(),
            "urgent": queryset.filter(priority="urgente").count(),
        }

        return super().changelist_view(request, extra_context)

    actions = ["mark_completed", "mark_cancelled", "mark_in_progress"]

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

    def mark_in_progress(self, request, queryset):
        """Marca projetos como em progresso."""
        updated = queryset.update(status=Project.Status.IN_PROGRESS)
        self.message_user(
            request,
            _("{count} projet(s) marqué(s) comme en cours.").format(count=updated),
        )

    mark_in_progress.short_description = _("Marquer comme en cours")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Administração de produtos."""

    list_display = [
        "code",
        "name",
        "type_produit",
        "unit",
        "price_unit",
        "is_active",
        "created_at",
    ]
    list_filter = [
        "type_produit",
        "unit",
        "is_active",
        "created_at",
    ]
    search_fields = [
        "code",
        "name",
        "description",
    ]
    date_hierarchy = "created_at"
    ordering = ["type_produit", "name"]
    fieldsets = (
        (
            _("Informations générales"),
            {
                "fields": (
                    "code",
                    "name",
                    "description",
                    "type_produit",
                    "is_active",
                )
            },
        ),
        (
            _("Prix et unité"),
            {
                "fields": (
                    "unit",
                    "price_unit",
                )
            },
        ),
        (
            _("Métadonnées"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ["code", "created_at", "updated_at"]


class DevisLineInline(admin.TabularInline):
    """Inline pour les lignes de devis."""

    model = DevisLine
    extra = 1
    fields = ["product", "quantity", "unit_price", "total", "description", "order"]
    readonly_fields = ["total_line"]


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    """Administração de devis."""

    list_display = [
        "reference",
        "title",
        "project_title",
        "project_client",
        "status_colored",
        "total",
        "date_created",
        "date_expiry",
    ]
    list_filter = [
        "status",
        "date_created",
        "date_expiry",
        "tax_rate",
        "project__project_type",
        "project__status",
    ]
    search_fields = [
        "reference",
        "title",
        "description",
        "project__title",
        "project__reference",
        "project__user__email",
    ]
    date_hierarchy = "date_created"

    fieldsets = (
        (
            _("Informations générales"),
            {
                "fields": (
                    "reference",
                    "title",
                    "project",
                    "created_by",
                    "description",
                    "status",
                )
            },
        ),
        (
            _("Dates et validité"),
            {
                "fields": (
                    "date_created",
                    "date_sent",
                    "date_viewed",
                    "date_response",
                    "date_expiry",
                )
            },
        ),
        (
            _("Montants"),
            {
                "fields": (
                    "subtotal",
                    "tax_rate",
                    "tax_amount",
                    "total",
                )
            },
        ),
        (
            _("Notes et conditions"),
            {
                "fields": (
                    "terms_conditions",
                    "notes",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Métadonnées"),
            {
                "fields": ("date_updated",),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = [
        "reference",
        "date_created",
        "date_updated",
        "subtotal",
        "tax_amount",
        "total",
    ]

    inlines = [DevisLineInline]

    def project_title(self, obj):
        """Retorna o título do projeto."""
        return obj.project.title

    project_title.short_description = _("Projet")
    project_title.admin_order_field = "project__title"

    def project_client(self, obj):
        """Retorna o email do client."""
        return obj.project.user.email

    project_client.short_description = _("Client")
    project_client.admin_order_field = "project__user__email"

    def status_colored(self, obj):
        """Exibe o status com cores."""
        colors = {
            "brouillon": "#6B7280",
            "envoye": "#3B82F6",
            "vu": "#8B5CF6",
            "accepte": "#10B981",
            "refuse": "#EF4444",
            "expire": "#F97316",
            "annule": "#EF4444",
        }

        color = colors.get(obj.status, "#6B7280")
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = _("Statut")
    status_colored.admin_order_field = "status"

    def get_queryset(self, request):
        """Otimiza queries."""
        return (
            super()
            .get_queryset(request)
            .select_related("project", "project__user", "created_by")
        )

    actions = ["mark_sent", "mark_expired", "recalculate_totals"]

    def mark_sent(self, request, queryset):
        """Marca devis como enviados."""
        from django.utils import timezone

        updated = queryset.filter(status="brouillon").update(
            status=Devis.Status.SENT, date_sent=timezone.now()
        )
        self.message_user(
            request,
            _("{count} devis marqué(s) comme envoyé(s).").format(count=updated),
        )

    mark_sent.short_description = _("Marquer comme envoyé")

    def mark_expired(self, request, queryset):
        """Marca devis como expirados."""
        updated = queryset.filter(status__in=["envoye", "vu"]).update(
            status=Devis.Status.EXPIRED
        )
        self.message_user(
            request,
            _("{count} devis marqué(s) comme expiré(s).").format(count=updated),
        )

    mark_expired.short_description = _("Marquer comme expiré")

    def recalculate_totals(self, request, queryset):
        """Recalcula os totais dos devis."""
        count = 0
        for devis in queryset:
            devis.calculate_totals()
            count += 1

        self.message_user(
            request,
            _("{count} devis recalculé(s).").format(count=count),
        )

    recalculate_totals.short_description = _("Recalculer les totaux")


@admin.register(DevisHistory)
class DevisHistoryAdmin(admin.ModelAdmin):
    """Administração do histórico de devis."""

    list_display = [
        "devis_reference",
        "action",
        "user",
        "timestamp",
    ]
    list_filter = [
        "action",
        "timestamp",
    ]
    search_fields = [
        "devis__reference",
        "devis__title",
        "user__email",
        "notes",
    ]
    date_hierarchy = "timestamp"

    fieldsets = (
        (
            _("Informations"),
            {
                "fields": (
                    "devis",
                    "action",
                    "user",
                    "timestamp",
                    "notes",
                )
            },
        ),
    )

    readonly_fields = ["timestamp"]

    def devis_reference(self, obj):
        """Retorna a referência do devis."""
        return obj.devis.reference

    devis_reference.short_description = _("Devis")
    devis_reference.admin_order_field = "devis__reference"

    def get_queryset(self, request):
        """Otimiza queries."""
        return super().get_queryset(request).select_related("devis", "user")
