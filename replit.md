# LOPES PEINTURE - Django Project on Replit

## Project Overview
This is a complete Django-based web application for "LOPES PEINTURE," a French painting company. The system provides comprehensive project management, user authentication, and administrative dashboards.

## ✅ Setup Completed
### Backend (Django 5.2.5)
- **Dependencies**: All Python packages installed from requirements.txt (Django, django-allauth, Tailwind, etc.)
- **Database**: SQLite configured for development, PostgreSQL ready for production
- **Authentication**: Custom user model with email-based login, social authentication ready (Google/Facebook)
- **Admin**: Custom admin interface with user management and permissions
- **Static Files**: Configured with WhiteNoise for production serving

### Frontend (Tailwind CSS)
- **Styling**: Tailwind CSS 3.8.0 properly configured and built
- **Templates**: Complete responsive templates for authentication, dashboard, and project management
- **Static Assets**: All CSS, JavaScript, and images properly served
- **Node.js**: Version 20 installed with all NPM dependencies

### Environment Configuration
- **Port**: Django development server running on port 5000 (required for Replit)
- **Hosts**: Configured to accept all hosts (`*`) for development
- **CORS**: Properly configured for cross-origin requests
- **Security**: Production security settings configured with appropriate cookie policies

### Database Setup
- **Migrations**: All database migrations applied successfully
- **Initial Data**: Site setup completed with default superuser and user groups
- **Permissions**: Three user groups configured (CLIENTS, COLLABORATORS, ADMINISTRATORS)

## 🔐 Default Credentials
- **Superuser Email**: admin@lopespeinture.com
- **Password**: admin123
- ⚠️ **Important**: Change password after first login!

## 🚀 Deployment Configuration
- **Build Command**: Tailwind CSS compilation + static files collection
- **Run Command**: Gunicorn WSGI server configured for production
- **Static Files**: WhiteNoise configured for efficient static file serving
- **Security**: Production-ready security headers and settings

## 🛠️ Key Features
### User Management
- Custom user model with email authentication
- User profiles with avatars and contact information
- Role-based permissions (Client, Collaborator, Administrator)
- Social authentication ready (Google, Facebook)

### Project Management
- Complete CRUD operations for projects
- Quote/estimate (devis) system
- Status tracking and workflow management
- Document management and file uploads

### Admin Dashboard
- Custom admin interface with statistics
- User management and group permissions
- Real-time metrics and reporting
- Visual dashboard with charts and progress tracking

## 📁 Project Structure
```
├── accounts/          # User authentication and management
├── profiles/          # User profiles and settings
├── projects/          # Project and quote management
├── pages/            # Static pages and public content
├── core/             # Django settings and configuration
├── templates/        # HTML templates
├── static/           # Static assets (CSS, JS, images)
├── tema_lopes_peinture_tailwind/  # Tailwind CSS theme
└── media/            # User uploads and media files
```

## 🔧 Development Commands
- **Run Server**: `python manage.py runserver 0.0.0.0:5000`
- **Build Tailwind**: `cd tema_lopes_peinture_tailwind/static_src && npm run build`
- **Collect Static**: `python manage.py collectstatic --noinput`
- **Create Migrations**: `python manage.py makemigrations`
- **Apply Migrations**: `python manage.py migrate`

## 🔒 Security Considerations
The application includes production-ready security features:
- CSRF protection enabled
- Secure cookie configurations
- XSS protection headers
- HTTPS redirection for production
- Input validation and sanitization

## 📝 Notes for Git Commit
Before committing to git, you should manually run:
```bash
git rm --cached db.sqlite3
git rm --cached -r media/
git rm --cached -r logs/
```
These files contain sensitive data and should not be versioned.

## 🌐 Access
The application is running at: http://localhost:5000
Login page: http://localhost:5000/login/

## Last Updated
September 22, 2025 - Complete Replit environment setup