# 📋 **Mapeamento de URLs - App Projects**

## **🏠 DASHBOARDS**
- `/projects/` → Dashboard principal do usuário
- `/projects/admin-dashboard/` → Dashboard administrativo (staff only)

## **📁 PROJETOS**
### **CRUD Básico:**
- `/projects/projets/` → Listagem de projetos (com filtros)
- `/projects/projets/nouveau/` → Criar novo projeto
- `/projects/projets/{uuid}/` → Visualizar projeto
- `/projects/projets/{uuid}/modifier/` → Editar projeto
- `/projects/projets/{uuid}/supprimer/` → Deletar projeto

### **Ações Especiais:**
- `/projects/projets/{uuid}/demander-devis/` → Solicitar orçamento
- `/projects/projets/{uuid}/update-status/` → Atualizar status (admin)

## **💰 DEVIS**
### **CRUD e Gestão:**
- `/projects/devis/` → Listagem de devis
- `/projects/devis/{uuid}/` → Visualizar devis
- `/projects/devis/{uuid}/modifier/` → Editar devis (admin)
- `/projects/devis/{uuid}/envoyer/` → Enviar devis (admin)
- `/projects/devis/{uuid}/repondre/` → Responder devis (cliente)

### **Criação:**
- `/projects/projets/{project_uuid}/creer-devis/` → Criar devis para projeto

## **🛠️ ADMINISTRAÇÃO**
### **Produtos:**
- `/projects/admin/produits/` → Listagem de produtos (admin)
- `/projects/admin/produits/nouveau/` → Criar produto (admin)
- `/projects/admin/produits/{uuid}/modifier/` → Editar produto (admin)

## **⚡ AJAX & API**
- `/projects/ajax/produit/{uuid}/prix/` → Buscar preço do produto
- `/projects/ajax/stats/` → Estatísticas dos projetos

## **🔍 BUSCA & FILTROS**
- `/projects/search/projets/` → Busca avançada de projetos
- `/projects/search/devis/` → Busca avançada de devis

## **📊 PERMISSÕES POR URL**
| URL Pattern | Usuário | Staff | Superuser |
|-------------|---------|-------|-----------|
| `/projects/` | ✅ | ✅ | ✅ |
| `/projects/admin-dashboard/` | ❌ | ✅ | ✅ |
| `/projects/projets/*` | ✅ (próprios) | ✅ (todos) | ✅ |
| `/projects/devis/*` | ✅ (próprios) | ✅ (todos) | ✅ |
| `/projects/admin/*` | ❌ | ✅ | ✅ |
| `/projects/ajax/*` | ✅ | ✅ | ✅ |

## **🎯 EXEMPLOS DE NAVEGAÇÃO**

### **Fluxo Cliente:**
1. `GET /projects/` → Dashboard
2. `GET /projects/projets/nouveau/` → Criar projeto
3. `POST /projects/projets/nouveau/` → Salvar projeto
4. `GET /projects/projets/{uuid}/` → Ver projeto criado
5. `POST /projects/projets/{uuid}/demander-devis/` → Solicitar orçamento
6. `GET /projects/devis/` → Ver devis recebidos
7. `GET /projects/devis/{uuid}/` → Ver devis específico
8. `POST /projects/devis/{uuid}/repondre/` → Aceitar/Recusar devis

### **Fluxo Admin:**
1. `GET /projects/admin-dashboard/` → Dashboard admin
2. `GET /projects/projets/` → Ver todos os projetos
3. `GET /projects/projets/{uuid}/` → Ver projeto específico
4. `GET /projects/projets/{project_uuid}/creer-devis/` → Criar devis
5. `POST /projects/projets/{project_uuid}/creer-devis/` → Salvar devis
6. `POST /projects/devis/{uuid}/envoyer/` → Enviar devis ao cliente
7. `GET /projects/admin/produits/` → Gerenciar produtos