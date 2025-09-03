from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    PasswordResetForm as DjangoPasswordResetForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import User


class UserRegistrationForm(UserCreationForm):
    """
    Formulário de registro de usuário personalizado.
    Permite criar novos usuários com validações específicas.
    """

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre email"),
                "autocomplete": "email",
            }
        ),
        help_text=_("Votre adresse email sera utilisée pour vous connecter."),
    )

    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre prénom"),
                "autocomplete": "given-name",
            }
        ),
    )

    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre nom"),
                "autocomplete": "family-name",
            }
        ),
    )

    account_type = forms.ChoiceField(
        choices=User.AccountType.choices,
        initial=User.AccountType.CLIENT,
        widget=forms.RadioSelect(
            attrs={
                "class": "form-radio text-blue-600",
            }
        ),
        label=_("Type de compte"),
        help_text=_("Sélectionnez le type de compte approprié."),
    )

    password1 = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre mot de passe"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )

    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Confirmez votre mot de passe"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Entrez le même mot de passe que précédemment, pour vérification."),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "account_type",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário com configurações personalizadas.
        """
        super().__init__(*args, **kwargs)

        # Tornar campos obrigatórios
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        # Personalizar mensagens de erro
        self.fields["email"].error_messages.update(
            {
                "required": _("L'adresse email est obligatoire."),
                "invalid": _("Veuillez entrer une adresse email valide."),
            }
        )

    def clean_password2(self):
        """
        Valida se as duas senhas coincidem.

        Returns:
            str: Segunda senha validada

        Raises:
            ValidationError: Se as senhas não coincidirem
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                _("Les deux mots de passe ne correspondent pas."),
                code="password_mismatch",
            )
        return password2

    def clean_email(self):
        """
        Valida se o email não está já em uso.

        Returns:
            str: Email validado e normalizado

        Raises:
            ValidationError: Se o email já estiver em uso
        """
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if User.objects.filter(email=email).exists():
                raise ValidationError(
                    _("Un compte avec cette adresse email existe déjà.")
                )
        return email

    def clean_first_name(self):
        """
        Valida e limpa o primeiro nome.

        Returns:
            str: Primeiro nome validado
        """
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            first_name = first_name.strip().title()
        return first_name

    def clean_last_name(self):
        """
        Valida e limpa o sobrenome.

        Returns:
            str: Sobrenome validado
        """
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            last_name = last_name.strip().title()
        return last_name

    def save(self, commit=True):
        """
        Salva o usuário com configurações específicas.

        Args:
            commit (bool): Se deve salvar no banco de dados

        Returns:
            User: Instância do usuário criado
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.account_type = self.cleaned_data["account_type"]

        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Formulário de login personalizado com validações de segurança.
    """

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre email"),
                "autocomplete": "email",
            }
        ),
    )

    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre mot de passe"),
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": _(
            "Veuillez saisir une adresse e-mail et un mot de passe valides. "
            "Notez que les deux champs sont sensibles à la casse."
        ),
        "inactive": _("Ce compte est inactif."),
        "locked_out": _(
            "Ce compte est temporairement verrouillé en raison de trop nombreuses tentatives de connexion échouées."
        ),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        Inicializa o formulário de login.

        Args:
            request: Requisição HTTP atual
        """
        super().__init__(request, *args, **kwargs)
        self.request = request

    def clean(self):
        """
        Valida as credenciais e verifica bloqueios de segurança.

        Returns:
            dict: Dados limpos do formulário

        Raises:
            ValidationError: Se as credenciais forem inválidas ou conta bloqueada
        """
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # Verificar se o usuário existe e não está bloqueado
            try:
                user = User.objects.get(email=username.lower())

                # Verificar se a conta está bloqueada
                if user.is_locked_out():
                    raise ValidationError(
                        self.error_messages["locked_out"],
                        code="locked_out",
                    )

                # Tentar autenticar
                self.user_cache = authenticate(
                    self.request,
                    username=username,
                    password=password,
                )

                if self.user_cache is None:
                    # Incrementar tentativas falhadas
                    ip_address = self.get_client_ip()
                    user.increment_failed_login(ip_address)

                    raise ValidationError(
                        self.error_messages["invalid_login"],
                        code="invalid_login",
                    )
                else:
                    # Reset tentativas falhadas em caso de sucesso
                    user.reset_failed_login()
                    self.confirm_login_allowed(self.user_cache)

            except User.DoesNotExist:
                raise ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

        return self.cleaned_data

    def get_client_ip(self):
        """
        Obtém o endereço IP do cliente.

        Returns:
            str: Endereço IP do cliente
        """
        if self.request:
            x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip = x_forwarded_for.split(",")[0]
            else:
                ip = self.request.META.get("REMOTE_ADDR")
            return ip
        return None


class UserChangeForm(UserChangeForm):
    """
    Formulário para edição de usuário no admin.
    """

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário de edição.
        """
        super().__init__(*args, **kwargs)
        # Remover o campo de senha do formulário de edição
        if "password" in self.fields:
            del self.fields["password"]


class PasswordResetForm(DjangoPasswordResetForm):
    """
    Formulário para solicitar redefinição de senha através do email.
    """

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre email"),
                "autocomplete": "email",
            }
        ),
        help_text=_("Entrez l'adresse email associée à votre compte."),
    )

    def clean_email(self):
        """
        Valida se existe um usuário ativo com o email fornecido.

        Returns:
            str: Email validado

        Raises:
            ValidationError: Se não houver conta ativa com o email
        """
        email = self.cleaned_data.get("email")
        if email:
            email = email.lower().strip()
            if not User.objects.filter(email=email, is_active=True).exists():
                raise ValidationError(
                    _("Aucun compte actif n'a été trouvé avec cette adresse email.")
                )
        return email

    def get_users(self, email):
        """
        Retorna usuários ativos com o email fornecido.

        Args:
            email (str): Email para buscar usuários

        Returns:
            QuerySet: Usuários encontrados
        """
        return User.objects.filter(
            email__iexact=email,
            is_active=True,
        )


class PasswordChangeForm(forms.Form):
    """
    Formulário para alteração de senha do usuário logado.
    """

    old_password = forms.CharField(
        label=_("Mot de passe actuel"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre mot de passe actuel"),
                "autocomplete": "current-password",
            }
        ),
    )

    new_password1 = forms.CharField(
        label=_("Nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
        help_text=_("Votre mot de passe doit contenir au moins 8 caractères."),
    )

    new_password2 = forms.CharField(
        label=_("Confirmation du nouveau mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Confirmez votre nouveau mot de passe"),
                "autocomplete": "new-password",
            }
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Inicializa o formulário com o usuário atual.

        Args:
            user (User): Usuário que está alterando a senha
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        """
        Valida se a senha atual está correta.

        Returns:
            str: Senha atual validada

        Raises:
            ValidationError: Se a senha atual estiver incorreta
        """
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError(
                _("Votre mot de passe actuel est incorrect."),
                code="password_incorrect",
            )
        return old_password

    def clean_new_password2(self):
        """
        Valida se as duas senhas novas coincidem.

        Returns:
            str: Nova senha validada

        Raises:
            ValidationError: Se as senhas não coincidirem
        """
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    _("Les deux mots de passe ne correspondent pas."),
                    code="password_mismatch",
                )
        return password2

    def save(self, commit=True):
        """
        Salva a nova senha do usuário.

        Args:
            commit (bool): Se deve salvar no banco de dados

        Returns:
            User: Usuário com senha atualizada
        """
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil básico do usuário.
    Focado apenas nos campos do modelo User.
    """

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "readonly": True,  # Email não deve ser editável após criação
            }
        ),
        help_text=_("L'email ne peut pas être modifié."),
    )

    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre prénom"),
            }
        ),
    )

    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre nom"),
            }
        ),
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário de perfil.
        """
        super().__init__(*args, **kwargs)

        # Tornar campos obrigatórios
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

    def clean_first_name(self):
        """
        Valida e limpa o primeiro nome.

        Returns:
            str: Primeiro nome validado
        """
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            first_name = first_name.strip().title()
        return first_name

    def clean_last_name(self):
        """
        Valida e limpa o sobrenome.

        Returns:
            str: Sobrenome validado
        """
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            last_name = last_name.strip().title()
        return last_name

    def clean(self):
        """
        Valida os dados do formulário.

        Returns:
            dict: Dados limpos do formulário

        Raises:
            ValidationError: Se houver erros de validação
        """
        cleaned_data = super().clean()
        if cleaned_data.get("birth_date"):
            if cleaned_data["birth_date"] > timezone.now().date():
                raise ValidationError(
                    _("La date de naissance ne peut pas être dans le futur")
                )
        return cleaned_data


class AccountDeleteForm(forms.Form):
    """
    Formulário para confirmação de exclusão de conta.
    """

    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-red-500 focus:ring-2 focus:ring-red-200",
                "placeholder": _("Entrez votre mot de passe pour confirmer"),
                "autocomplete": "current-password",
            }
        ),
        help_text=_(
            "Entrez votre mot de passe pour confirmer la suppression de votre compte."
        ),
    )

    confirm_deletion = forms.BooleanField(
        label=_("Je confirme vouloir supprimer définitivement mon compte"),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-checkbox text-red-600",
            }
        ),
        help_text=_(
            "Cette action est irréversible. Toutes vos données seront perdues."
        ),
    )

    def __init__(self, user, *args, **kwargs):
        """
        Inicializa o formulário com o usuário atual.

        Args:
            user (User): Usuário que está excluindo a conta
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password(self):
        """
        Valida se a senha está correta.

        Returns:
            str: Senha validada

        Raises:
            ValidationError: Se a senha estiver incorreta
        """
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise ValidationError(
                _("Mot de passe incorrect."),
                code="password_incorrect",
            )
        return password

    def clean_confirm_deletion(self):
        """
        Valida se a confirmação foi marcada.

        Returns:
            bool: Confirmação validada

        Raises:
            ValidationError: Se a confirmação não foi marcada
        """
        confirm = self.cleaned_data.get("confirm_deletion")
        if not confirm:
            raise ValidationError(
                _("Vous devez confirmer la suppression de votre compte."),
                code="confirmation_required",
            )
        return confirm
