# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

# Para desenvolvimento (com watch)
npm run watch-css


# Para build único
npm run build-css

# Para produção (minificado)
npm run build-css-prod


# Criar e aplicar migrações
python manage.py makemigrations accounts
python manage.py migrate

# Criar superusuário
python manage.py create_superuser

# Ou usar o comando personalizado
python manage.py create_superuser --email admin@lopespeinture.fr --first-name Admin --last-name Lopes

# Executar testes
python manage.py test accounts

# Executar servidor de desenvolvimento
python manage.py runserver


backend/
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── create_superuser.py
│   └── migrations/
│       └── __init__.py
├── templates/
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── dashboard.html
│   │   ├── mes_projets.html
│   │   └── sections/
│   └── emails/
│       ├── welcome.html
│       └── password_reset.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
│   ├── avatars/
│   └── projetos/
└── logs/
    └── accounts.log

Desinstale os pacotes Python: No seu terminal (com o ambiente virtual ativado), execute:

pip uninstall django-tailwind django-browser-reload

Confirme com y se for solicitado.

Exclua a pasta theme: No explorador de arquivos do VS Code, clique com o botão direito na pasta theme e selecione "Delete".

Limpe o arquivo settings.py: Abra o arquivo [core/settings/base.py]base.py ) e remova todas as configurações relacionadas ao Tailwind que adicionamos. Seu arquivo deve ficar assim nessas seções:

// filepath: c:\Users\fabia\OneDrive\todos os projetos\Projetos\site_lopes_peinture\core\settings\base.py
// ...existing code...
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicações internas
    "accounts",
    # Pacotes de terceiros
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# REMOVA AS LINHAS TAILWIND_APP_NAME, INTERNAL_IPS e NPM_BIN_PATH DAQUI

ROOT_URLCONF = "core.urls"
// ...existing code...

Passo 2: Instalar Versões Estáveis
Agora vamos instalar versões específicas e estáveis dos pacotes.

No seu terminal, execute:

pip install django-tailwind==3.8.0 django-browser-reload

Passo 3: Configurar settings.py (Do jeito certo)
Agora, vamos adicionar a configuração de volta ao settings.py.


\settings\base.py
// ...existing code...
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicações internas
    "accounts",
    # Pacotes de terceiros
    "tailwind",
    "django_browser_reload",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware", # Adicione esta linha
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Adicione estas linhas no final da seção
TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = [
    "127.0.0.1",
]

NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"


ROOT_URLCONF = "core.urls"
// ...existing code...

Passo 4: Executar tailwind init
Este é o momento da verdade. Com tudo limpo e configurado, execute o comando de inicialização.

python manage.py tailwind init

Ele vai perguntar o nome da app. Pressione Enter para aceitar theme.
Ele vai perguntar sobre o daisyUI. Pressione Enter para aceitar no.
O comando agora deve criar a aplicação theme e os arquivos de configuração dentro dela.

Passo 5: Adicionar theme aos INSTALLED_APPS
Se o passo anterior funcionou, o tailwind init lhe dará uma instrução para adicionar 'theme' aos seus INSTALLED_APPS. Faça isso agora.

// ...existing code...
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicações internas
    "accounts",
    # Pacotes de terceiros
    "tailwind",
    "theme", # Adicione esta linha
    "django_browser_reload",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware", # Adicione esta linha
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# Adicione estas linhas no final da seção
TAILWIND_APP_NAME = "theme"

INTERNAL_IPS = [
    "127.0.0.1",
]

NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"


ROOT_URLCONF = "core.urls"
// ...existing code...

Passo 6: Instalar as Dependências do Node
Finalmente, execute o comando de instalação do Tailwind.

python manage.py tailwind install

Se todos esses passos forem concluídos sem erros, sua configuração estará correta e pronta para uso. O próximo passo será configurar o tailwind.config.js e iniciar os servidores.

Similar code found with 3 license types - View matches


Agora vamos para os próximos passos para finalizar a configuração.

Passo 1: Ajustar o tailwind.config.js
O arquivo gerado é ótimo, mas para garantir que ele capture todas as classes, vamos simplificar e ativar a verificação de arquivos Python. Substitua o conteúdo do seu tailwind.config.js por este:

/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        '../../**/templates/**/*.html',
        '../../**/*.py' // Ativa a verificação em arquivos Python
    ],
    theme: {
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}

Passo 2: Atualizar os Templates Base
Agora, vamos modificar seus arquivos base.html e base_auth.html para que eles usem o CSS compilado pelo Tailwind, em vez do link CDN.


jetos\site_lopes_peinture\templates\base.html
{% load static %}
{% load tailwind_tags %}

<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>
    {% block title %}LOPES PEINTURE - Spécialiste Des Services De Peinture {% endblock %}
  </title>
  {% tailwind_css %}
  <link rel="stylesheet" href="{% static 'accounts/css/base.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>

  {% block extra_js %}{% endblock %}
  <script src="{% static 'accounts/js/base.js' %}"></script>
</body>
</html>

Passo 3: Iniciar o Ambiente de Desenvolvimento
A configuração está completa! Para trabalhar no seu projeto, você agora precisa rodar dois comandos, cada um em seu próprio terminal:

Terminal 1 - Compilador Tailwind: Este comando "assiste" seus arquivos em busca de mudanças e recompila o CSS automaticamente.


python manage.py tailwind start

Terminal 2 - Servidor Django: Este é o comando padrão para rodar seu site. O django-browser-reload irá recarregar a página no navegador automaticamente quando o CSS for recompilado.

python manage.py runserver

# 🎨 LOPES PEINTURE - Sistema de Gestão

Sistema web completo para gestão de clientes, colaboradores e projetos da empresa LOPES PEINTURE.

## 🚀 Funcionalidades

### 👥 Gestão de Usuários
- ✅ Sistema de autenticação personalizado
- ✅ Tipos de conta: Cliente, Colaborador, Administrador
- ✅ Perfis completos com foto e informações de contato
- ✅ Dashboard personalizado por tipo de usuário

### 🔐 Segurança
- ✅ Autenticação baseada em email
- ✅ Grupos e permissões personalizados
- ✅ Validações de formulário avançadas
- ✅ Proteção CSRF e XSS

### 🎨 Interface
- ✅ Design moderno com Tailwind CSS
- ✅ Responsivo para mobile/tablet/desktop
- ✅ Animações e transições suaves
- ✅ Dark mode pronto (estrutura)

### ⚙️ Administração
- ✅ Admin personalizado com estatísticas
- ✅ Dashboard com métricas em tempo real
- ✅ Gestão visual de usuários e perfis
- ✅ Relatórios e exportações

## 🛠️ Tecnologias

- **Backend**: Django 4.2+, Python 3.11+
- **Frontend**: Tailwind CSS, JavaScript ES6+
- **Banco**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Media**: Pillow para processamento de imagens
- **Testes**: pytest, coverage

## 📦 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd site_lopes_peinture
```

### 2. Crie ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Setup completo
```bash
# Windows
setup_complete.bat

# Ou manualmente
python manage.py setup_site
```

### 5. Execute o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

## 🔑 Credenciais Padrão

### Superusuário
- **Email**: admin@lopespeinture.com
- **Senha**: admin123
- ⚠️ **Mude após primeiro login!**

### Usuários de Teste
- **Clientes**: jean.dupont@email.com, marie.martin@email.com
- **Colaboradores**: paul.peintre@lopespeinture.com, ana.assistante@lopespeinture.com
- **Senha**: test123

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Com cobertura
coverage run --source='.' manage.py test
coverage report -m
coverage html

# Script automático
run_tests.bat
```

## 📁 Estrutura do Projeto

```
site_lopes_peinture/
├── accounts/           # App de usuários
│   ├── models.py      # Modelo User personalizado
│   ├── forms.py       # Formulários de auth
│   ├── views.py       # Views de login/registro
│   └── admin.py       # Admin personalizado
├── profiles/          # App de perfis
│   ├── models.py      # Modelo Profile
│   ├── forms.py       # Formulário de perfil
│   └── views.py       # Views de perfil
├── core/              # Configurações do projeto
├── templates/         # Templates HTML
├── static/            # Arquivos estáticos
├── media/             # Uploads de usuários
└── requirements.txt   # Dependências
```

## 🎯 Comandos Úteis

### Desenvolvimento
```bash
# Servidor de desenvolvimento
python manage.py runserver

# Shell Django
python manage.py shell

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate
```

### Gestão de Usuários
```bash
# Criar usuários de teste
python manage.py create_test_users --count=5

# Reset completo do banco
python manage.py reset_db --confirm
```

### Validação
```bash
# Verificar projeto
python validate_project.py

# Verificar configurações
python manage.py check --deploy
```

## 🚀 Deploy

### Preparação para produção
1. Configure `ALLOWED_HOSTS` em settings
2. Defina `DEBUG = False`
3. Configure banco PostgreSQL
4. Configure servidor de email
5. Execute `python manage.py collectstatic`

### Variáveis de ambiente
```bash
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## 📈 Performance

- ✅ Consultas otimizadas com `select_related`
- ✅ Cache de sessões configurado
- ✅ Compressão de assets estáticos
- ✅ Lazy loading de imagens

## 🔒 Segurança

- ✅ CSRF protection habilitado
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ Secure headers configurados
- ✅ Rate limiting pronto

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é propriedade da **LOPES PEINTURE**. Todos os direitos reservados.

## 📞 Suporte

- **Email**: support@lopespeinture.com
- **Telefone**: +33 1 23 45 67 89
- **Site**: https://lopespeinture.com

---

**Desenvolvido com ❤️ para LOPES PEINTURE**