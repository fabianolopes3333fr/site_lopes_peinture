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