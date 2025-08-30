from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Import signals inside ready() to avoid premature imports
        from .signals import create_default_groups
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_groups, sender=self)

        # Import other signals
        import accounts.signals
