# Testes do Sistema Accounts

## Status Atual
✅ **19/19 testes passando**

## Cobertura de Testes

### Views Testadas:
- ✅ RegisterView (GET/POST)
- ✅ LoginView (GET/POST)
- ✅ DashboardView (proteção de acesso)

### Formulários Testados:
- ✅ UserRegistrationForm (validação)
- ✅ UserLoginForm (autenticação)

### Modelos Testados:
- ✅ User (criação, validação)
- ✅ Account types (CLIENT, COLLABORATOR, ADMIN)

### URLs Testadas:
- ✅ /accounts/register/
- ✅ /accounts/login/
- ✅ /accounts/dashboard/

### Signals Testados:
- ✅ Atribuição automática de grupos
- ✅ Log de criação de usuários
- ✅ Envio de emails (com fallback)

## Executar Testes

```bash
# Todos os testes
python manage.py test accounts -v 2

python manage.py test accounts --debug-mode -v 2
# Testes específicos
python manage.py test accounts.tests.SimpleTestCase -v 2

# Testar signals
python manage.py test accounts.tests.SignalsTestCase -v 2

# Testar apenas a classe com problemas
python manage.py test accounts.tests.FormTestCase.test_registration_form_password_validation -v 2

# Testar apenas emails
python manage.py test accounts.tests.SignalsTestCase.test_welcome_email_sent_for_active_user -v 2

# Com cobertura
coverage run manage.py test accounts
coverage report
```

## Problemas Conhecidos
- ⚠️ Cache Redis não disponível em testes (usando dummy cache)
- ⚠️ Templates de email em desenvolvimento


# 1. Deletar banco
del db.sqlite3

# 2. Remover migrações problemáticas
python manage.py migrate accounts zero --fake

# 3. Deletar arquivos de migração
# Vá para accounts/migrations/ e delete todos exceto __init__.py

# 4. Criar novas migrações
python manage.py makemigrations accounts

# 5. Aplicar migrações
python manage.py migrate


# via script 

# Executar o script de reset
python reset_migrations.py

# OU fazer manualmente:
# 1. Deletar banco
del db.sqlite3

# 2. Ir para pasta de migrações e deletar arquivos problemáticos
cd accounts\migrations
# Deletar todos os arquivos 0002_*, 0003_*, etc. (manter apenas __init__.py)

cd ..\..

# 3. Criar novas migrações
python manage.py makemigrations accounts

# 4. Aplicar migrações
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser --email admin@lopespeinture.com

# 6. Executar testes
python manage.py test accounts


@echo off
echo ==========================================
echo    🚀 APLICANDO MIGRAÇÕES - LOPES PEINTURE
echo ==========================================
echo.

echo 📝 Verificando migrações pendentes...
python manage.py showmigrations

echo.
echo 🔄 Criando migrações para accounts...
python manage.py makemigrations accounts

echo.
echo 🔄 Criando migrações para profiles...
python manage.py makemigrations profiles

echo.
echo 🔄 Criando migrações para outros apps...
python manage.py makemigrations

echo.
echo 📊 Verificando plano de migração...
python manage.py migrate --plan

echo.
echo ✅ Aplicando migrações...
python manage.py migrate

echo.
echo 🎯 Migrações concluídas!
pause


@echo off
title SETUP COMPLETO - LOPES PEINTURE
color 0A

echo.
echo ==========================================
echo    🎨 SETUP COMPLETO - LOPES PEINTURE
echo ==========================================
echo.

echo 📋 Este script vai executar o setup completo:
echo    1. Criar e aplicar migrações
echo    2. Configurar grupos e permissões
echo    3. Criar superusuário
echo    4. Criar usuários de teste
echo    5. Coletar arquivos estáticos
echo.

set /p confirm="Deseja continuar? (s/N): "
if /i not "%confirm%"=="s" goto :end

echo.
echo ==========================================
echo 📝 ETAPA 1: MIGRAÇÕES
echo ==========================================

echo 🔄 Removendo migrações antigas (se existirem)...
if exist "accounts\migrations\0001_initial.py" del "accounts\migrations\0001_initial.py" /Q
if exist "profiles\migrations\0001_initial.py" del "profiles\migrations\0001_initial.py" /Q

echo 🔄 Criando novas migrações...
python manage.py makemigrations accounts
python manage.py makemigrations profiles
python manage.py makemigrations

echo 📊 Aplicando migrações...
python manage.py migrate

echo.
echo ==========================================
echo ⚙️ ETAPA 2: CONFIGURAÇÃO INICIAL
echo ==========================================

echo 🚀 Executando setup do site...
python manage.py setup_site --admin-email=admin@lopespeinture.com --admin-password=admin123

echo.
echo ==========================================
echo 👥 ETAPA 3: USUÁRIOS DE TESTE
echo ==========================================

set /p create_test="Criar usuários de teste? (s/N): "
if /i "%create_test%"=="s" (
    echo 🧪 Criando usuários de teste...
    python manage.py create_test_users --count=3 --password=test123
)

echo.
echo ==========================================
echo 📦 ETAPA 4: ARQUIVOS ESTÁTICOS
echo ==========================================

echo 📦 Coletando arquivos estáticos...
python manage.py collectstatic --noinput

echo.
echo ==========================================
echo ✅ SETUP CONCLUÍDO COM SUCESSO!
echo ==========================================
echo.
echo 📋 INFORMAÇÕES IMPORTANTES:
echo.
echo 👑 SUPERUSUÁRIO:
echo    Email: admin@lopespeinture.com
echo    Senha: admin123
echo    ⚠️  MUDE A SENHA APÓS O PRIMEIRO LOGIN!
echo.
if /i "%create_test%"=="s" (
    echo 🧪 USUÁRIOS DE TESTE:
    echo    Clientes: jean.dupont@email.com, marie.martin@email.com, pierre.durand@email.com
    echo    Colaboradores: paul.peintre@lopespeinture.com, ana.assistante@lopespeinture.com, carlos.chef@lopespeinture.com
    echo    Senha para todos: test123
    echo.
)
echo 🌐 PRÓXIMOS PASSOS:
echo    1. Execute: python manage.py runserver
echo    2. Acesse: http://127.0.0.1:8000/
echo    3. Faça login com as credenciais acima
echo    4. Configure seu perfil
echo.

:end
pause