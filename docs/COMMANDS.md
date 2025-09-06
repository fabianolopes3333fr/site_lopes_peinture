# 🎯 COMANDOS ÚTEIS - LOPES PEINTURE

## 🚀 Setup Inicial

### Setup Completo (Recomendado)
```bash
# Windows
setup_complete.bat

# Ou manualmente
python manage.py setup_site
```

### Setup Passo a Passo
```bash
# 1. Criar migrações
python manage.py makemigrations
python manage.py migrate

# 2. Configurar site
python manage.py setup_site

# 3. Criar usuários de teste (opcional)
python manage.py create_test_users

# 4. Coletar estáticos
python manage.py collectstatic
```

## 👥 Gerenciamento de Usuários

### Criar Superusuário
```bash
python manage.py setup_site --admin-email=seu@email.com --admin-password=suasenha
```

### Criar Usuários de Teste
```bash
# Criar 5 usuários de cada tipo
python manage.py create_test_users --count=5 --password=test123

# Criar apenas 2 de cada tipo
python manage.py create_test_users --count=2
```

## 🔄 Migrações

### Criar e Aplicar Migrações
```bash
# Criar migrações específicas
python manage.py makemigrations accounts
python manage.py makemigrations profiles

# Aplicar todas
python manage.py migrate

# Ver status
python manage.py showmigrations
```

### Reset Completo do Banco
```bash
# ⚠️ CUIDADO: Deleta tudo!
python manage.py reset_db --confirm
```

## 🧪 Desenvolvimento

### Servidor de Desenvolvimento
```bash
python manage.py runserver
# Acesse: http://127.0.0.1:8000/
```

### Shell Django
```bash
python manage.py shell
```

### Verificar Configurações
```bash
python manage.py check
python manage.py check --deploy
```

## 📊 Informações do Sistema

### Estatísticas de Usuários
```python
# No shell Django
from django.contrib.auth import get_user_model
User = get_user_model()

print(f"Total: {User.objects.count()}")
print(f"Clients: {User.objects.filter(account_type='CLIENT').count()}")
print(f"Collaborators: {User.objects.filter(account_type='COLLABORATOR').count()}")
print(f"Admins: {User.objects.filter(account_type='ADMINISTRATOR').count()}")
```

### Verificar Grupos e Permissões
```python
from django.contrib.auth.models import Group, Permission

for group in Group.objects.all():
    print(f"{group.name}: {group.permissions.count()} permissões")
```

## 🎨 Tailwind CSS

### Desenvolvimento
```bash
# Se usando django-tailwind
python manage.py tailwind start
```

### Build para Produção
```bash
python manage.py tailwind build
```

## 📝 Logs e Debug

### Ver Logs
```bash
# Windows
type logs\django.log

# Linux/Mac
tail -f logs/django.log
```

## 🔧 Credenciais Padrão

### Superusuário
- **Email:** admin@lopespeinture.com
- **Senha:** admin123
- **⚠️ Mude após primeiro login!**

### Usuários de Teste
- **Clientes:** jean.dupont@email.com, marie.martin@email.com, etc.
- **Colaboradores:** paul.peintre@lopespeinture.com, ana.assistante@lopespeinture.com, etc.
- **Senha:** test123