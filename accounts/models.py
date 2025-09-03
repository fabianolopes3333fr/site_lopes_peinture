from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from django.core.validators import RegexValidator
from django.utils.functional import cached_property


class CustomUserManager(BaseUserManager):
    """
    Gerenciador personalizado para o modelo User.
    Responsável por criar usuários e superusuários com validações adequadas.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário regular com email e senha.

        Args:
            email (str): Email do usuário (obrigatório)
            password (str): Senha do usuário
            **extra_fields: Campos adicionais do usuário

        Returns:
            User: Instância do usuário criado

        Raises:
            ValueError: Se o email não for fornecido
        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário com permissões administrativas.

        Args:
            email (str): Email do superusuário
            password (str): Senha do superusuário
            **extra_fields: Campos adicionais do usuário

        Returns:
            User: Instância do superusuário criado

        Raises:
            ValueError: Se is_staff ou is_superuser não forem True
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("account_type", "ADMINISTRATOR")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário personalizado que utiliza email como identificador único.
    Suporta diferentes tipos de conta (Cliente, Colaborador, Administrador).
    Focado apenas na autenticação e informações básicas do usuário.
    """

    class AccountType(models.TextChoices):
        """Tipos de conta disponíveis no sistema."""

        CLIENT = "CLIENT", _("Client")
        COLLABORATOR = "COLLABORATOR", _("Collaborateur")
        ADMINISTRATOR = "ADMINISTRATOR", _("Administrateur")

    # Campos principais de autenticação
    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    # Adicionar validação de formato de telefone
    # phone = models.CharField(
    #     max_length=20,
    #     validators=[phone_regex]  # Adicionar validator
    # )

    account_type = models.CharField(
        _("type de compte"),
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CLIENT,
        help_text=_("Définit le niveau d'accès de l'utilisateur"),
    )

    # Informações pessoais básicas
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    # Campos de status e controle do Django
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    # Campos de auditoria e segurança
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True,
        help_text=_("Token para verificação de email"),
    )
    is_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Indica se o email foi verificado"),
    )

    # Campos de segurança para controle de login
    last_login_ip = models.GenericIPAddressField(
        _("last login IP"),
        null=True,
        blank=True,
        help_text=_("Último endereço IP de login"),
    )
    failed_login_attempts = models.PositiveIntegerField(
        _("failed login attempts"),
        default=0,
        help_text=_("Número de tentativas de login falhadas"),
    )
    last_failed_login = models.DateTimeField(
        _("last failed login"),
        null=True,
        blank=True,
        help_text=_("Data da última tentativa de login falhada"),
    )
    password_changed_at = models.DateTimeField(
        _("password changed at"),
        null=True,
        blank=True,
        help_text=_("Data da última alteração de senha"),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["account_type"]),
            models.Index(fields=["is_active"]),
        ]
        permissions = [
            ("can_view_dashboard", "Peut afficher le tableau de bord"),
            ("can_manage_users", "Peut gérer les utilisateurs"),
        ]

    def __str__(self):
        """Representação string do usuário."""
        return self.email

    def get_full_name(self):
        """
        Retorna o nome completo do usuário.

        Returns:
            str: Nome completo (primeiro nome + sobrenome) ou email se não houver nome
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        """
        Retorna o primeiro nome do usuário.

        Returns:
            str: Primeiro nome do usuário ou email se não houver primeiro nome
        """
        return self.first_name or self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Envia um email para este usuário.

        Args:
            subject (str): Assunto do email
            message (str): Conteúdo do email
            from_email (str): Email do remetente
            **kwargs: Argumentos adicionais para send_mail
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def increment_failed_login(self, ip_address=None):
        """
        Incrementa o contador de tentativas de login falhadas.

        Args:
            ip_address (str, optional): Endereço IP da tentativa de login
        """
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address

        update_fields = ["failed_login_attempts", "last_failed_login"]
        if ip_address:
            update_fields.append("last_login_ip")

        self.save(update_fields=update_fields)

    def reset_failed_login(self):
        """Reseta o contador de tentativas de login falhadas."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.save(update_fields=["failed_login_attempts", "last_failed_login"])

    def is_locked_out(self):
        """
        Verifica se o usuário está bloqueado devido a muitas tentativas falhadas.

        Returns:
            bool: True se o usuário estiver bloqueado
        """
        max_attempts = getattr(settings, "MAX_FAILED_LOGIN_ATTEMPTS", 5)

        if self.failed_login_attempts >= max_attempts:
            if self.last_failed_login:
                lockout_period = timezone.now() - timezone.timedelta(minutes=30)
                return self.last_failed_login >= lockout_period
        return False

    def set_password(self, raw_password):
        """
        Override para registrar quando a senha foi alterada.

        Args:
            raw_password (str): Nova senha em texto plano
        """
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()

    @cached_property
    def full_name(self):
        """
        Propriedade cached para o nome completo.

        Returns:
            str: Nome completo do usuário
        """
        return self.get_full_name()

    def clean(self):
        """
        Validações customizadas do modelo.

        Raises:
            ValidationError: Se alguma validação falhar
        """
        super().clean()

        # Validar email
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        """
        Override do método save para executar validações antes de salvar.
        """
        self.clean()
        super().save(*args, **kwargs)

    # Propriedades de conveniência para verificar tipo de conta
    @property
    def is_admin(self):
        """
        Verifica se o usuário é um administrador.

        Returns:
            bool: True se for administrador
        """
        return self.account_type == self.AccountType.ADMINISTRATOR

    @property
    def is_collaborator(self):
        """
        Verifica se o usuário é um colaborador.

        Returns:
            bool: True se for colaborador
        """
        return self.account_type == self.AccountType.COLLABORATOR

    @property
    def is_client(self):
        """
        Verifica se o usuário é um cliente.

        Returns:
            bool: True se for cliente
        """
        return self.account_type == self.AccountType.CLIENT

    def has_permission(self, permission_name):
        """
        Verifica se o usuário tem uma permissão específica baseada no tipo de conta.

        Args:
            permission_name (str): Nome da permissão a verificar

        Returns:
            bool: True se o usuário tiver a permissão
        """
        if self.is_admin:
            return True

        # Definir permissões específicas por tipo de conta
        collaborator_permissions = ["view_projects", "edit_projects", "view_clients"]

        if self.is_collaborator and permission_name in collaborator_permissions:
            return True

        return False

    def get_profile(self):
        from profiles.models import UserProfile

        return self.profile
