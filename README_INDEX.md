# 📚 Dadgan Legal Institution - Project Documentation Index

## 📖 Getting Started

1. **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Complete installation and usage guide
   - Setup instructions
   - Command reference
   - Model documentation
   - SEO features
   - Data import procedures

2. **[COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md)** - Project completion overview
   - What was accomplished
   - Statistics and metrics
   - Next steps
   - Key files created

## 🚀 Quick Start

```bash
# 1. Setup environment
./manage_site.sh setup

# 2. Start server
./manage_site.sh start

# 3. Access site
# Open: http://127.0.0.1:8000
# Admin: http://127.0.0.1:8000/admin
# Login: admin / admin123
```

## 🛠️ Management Scripts

### `./manage_site.sh` - Project Lifecycle
Controls Django server startup, shutdown, and restart.

**Commands:**
```bash
./manage_site.sh setup       # Create virtual environment and install dependencies
./manage_site.sh start       # Start Django development server
./manage_site.sh stop        # Stop running server
./manage_site.sh restart     # Restart server
./manage_site.sh status      # Check server status
./manage_site.sh help        # Show help message
```

### `./check_and_fix.sh` - System Diagnostics
Checks for missing dependencies and fixes issues.

**Commands:**
```bash
./check_and_fix.sh check     # Run diagnostic checks
./check_and_fix.sh fix       # Attempt to fix detected issues
./check_and_fix.sh full      # Check and fix with confirmation
```

### `./migrate_from_laravel.sh` - Remote Data Migration
Extracts data from legacy Laravel/WordPress server via SSH.

**Commands:**
```bash
./migrate_from_laravel.sh test          # Test SSH connection
./migrate_from_laravel.sh export-db     # Export databases only
./migrate_from_laravel.sh export-app    # Export Laravel app
./migrate_from_laravel.sh full          # Complete migration
```

## 📊 Data & Extraction

### `extract_data_final.py` - Data Extraction
Parses SQL dumps and extracts data to JSON format.

```bash
python3 extract_data_final.py

# Output:
# - data_extraction/qa_posts.json (50 records)
# - data_extraction/wordpress_posts.json
```

### `lawfirm/management/commands/import_qa_data.py` - Data Import
Django management command to import Q&A data into database.

```bash
python manage.py import_qa_data

# Options:
# --qa-file PATH          Specify custom JSON file
# --skip-existing         Skip already imported questions
```

## 🔍 SEO Implementation

### `lawfirm/seo.py` - SEO Utilities
Provides SEO metadata generation and Schema.org markup.

**Features:**
- `SEOMixin` - Context processor for SEO data
- `render_seo_meta_tags()` - Generate meta tags
- `render_question_schema()` - FAQ Schema.org markup
- `render_article_schema()` - Article Schema.org markup

### `lawfirm/templatetags/seo_tags.py` - Template Tags
Django template tags for rendering SEO metadata in templates.

**Tags:**
```django
{% load seo_tags %}

{# Filters #}
{{ object|seo_title }}
{{ object|seo_description }}
{{ object|seo_keywords }}

{# Template tags #}
{% question_schema question %}
{% article_schema article %}
{% organization_schema %}
{% breadcrumb_schema breadcrumbs %}
```

## 📁 Key Files

### Configuration
- `pyproject.toml` - Project metadata and dependencies
- `dadgan_project/settings.py` - Django settings
- `dadgan_project/urls.py` - URL routing

### Models & Logic
- `lawfirm/models.py` - Database models with SEO fields
- `lawfirm/views.py` - View logic with SEO context
- `lawfirm/forms.py` - Django forms
- `lawfirm/admin.py` - Admin interface

### Data
- `laravel_backup/` - Exported databases from remote server
  - `c1dadgan.sql` - WordPress database (1.5 MB)
  - `c1faq.sql` - Q&A database (23 KB)
- `data_extraction/` - Extracted and processed data
  - `qa_posts.json` - 50 Q&A records
  - `wordpress_posts.json` - Blog posts

### Migrations
- `lawfirm/migrations/0001_initial.py` - Initial schema
- `lawfirm/migrations/0002_*.py` - SEO fields

## 📊 Database Models

### BlogPost
```python
- id: Primary Key
- title: CharField(200)
- slug: SlugField(200, unique)
- author: ForeignKey(User)
- category: ForeignKey(Category)
- content: TextField
- excerpt: TextField(300)
- image: ImageField (optional)
- published: Boolean
- featured: Boolean
- views: PositiveIntegerField
- created_at: DateTimeField
- updated_at: DateTimeField
- seo_title: CharField(60)         # NEW
- seo_description: CharField(160)  # NEW
- seo_keywords: CharField(255)     # NEW
```

### Question
```python
- id: Primary Key
- title: CharField(200)
- slug: SlugField(200, unique)
- content: TextField
- asker_name: CharField(100)
- asker_email: EmailField
- category: ForeignKey(QACategory)
- views: PositiveIntegerField
- votes: IntegerField
- is_answered: Boolean
- is_published: Boolean
- created_at: DateTimeField
- updated_at: DateTimeField
- seo_title: CharField(60)         # NEW
- seo_description: CharField(160)  # NEW
- seo_keywords: CharField(255)     # NEW
```

### Answer
```python
- question: ForeignKey(Question)
- content: TextField
- answerer_name: CharField(100)
- answerer_title: CharField(100)
- votes: IntegerField
- is_best_answer: Boolean
- is_published: Boolean
- created_at: DateTimeField
- updated_at: DateTimeField
```

## 🎯 SEO Features

### Target Keyword
**"موسسه حقوقی"** (Legal Institution)

### Automatic SEO Methods
- `get_seo_title()` - Smart title generation with fallback
- `get_seo_description()` - Auto-generate from content if not set
- `get_seo_keywords()` - Combine custom + automatic keywords

### Schema.org Support
- FAQ Schema (Questions & Answers)
- Article Schema (Blog Posts)
- Organization Schema (Company Info)
- Breadcrumb Schema (Navigation)

## 🔗 Important URLs

### Development Server
- **Main Site**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin
- **Blog**: http://127.0.0.1:8000/blog/
- **Q&A**: http://127.0.0.1:8000/qa/

### Remote Data Sources
- **Server**: ssh rocky@37.32.13.22
- **WordPress DB**: c1dadgan (Docker: dadgan_app)
- **FAQ DB**: c1faq (Docker: dadgan_app)
- **MariaDB**: docker-mariadb-phpmyadmin-mariadb-1

## 📝 Important Notes

### Data Migration
- ✅ 29 Q&A questions successfully imported
- ✅ Original Farsi content preserved
- ✅ Parent-child relationships maintained
- ✅ View counts and metadata preserved

### SEO Optimization
- ✅ Schema.org structured data implemented
- ✅ Meta tags automatically generated
- ✅ Farsi content fully supported
- ✅ SEO keyword targeting configured

### Security
- ✅ CSRF protection enabled
- ✅ SQL injection prevention via ORM
- ✅ XSS protection in templates
- ✅ Admin authentication required
- ⚠️ Change default admin password in production

### Performance
- ✅ Database query optimization
- ✅ Image optimization with Pillow
- ✅ Static file serving configured
- ⚠️ Consider caching for production

## 🚀 Production Deployment

### Prerequisites
1. PostgreSQL database
2. gunicorn or uWSGI server
3. Nginx or Apache reverse proxy
4. SSL/HTTPS certificate

### Steps
```bash
# 1. Configure environment
export DEBUG=False
export ALLOWED_HOSTS=dadgan.com,www.dadgan.com
export SECRET_KEY=your-secret-key

# 2. Collect static files
python manage.py collectstatic

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start server
gunicorn dadgan_project.wsgi:application
```

See SETUP_GUIDE.md for detailed production deployment instructions.

## 💡 Tips & Tricks

### Adding New Questions
```bash
# Via admin
1. Go to http://127.0.0.1:8000/admin
2. Add Question
3. Fill in fields including SEO fields
4. Save and publish

# Via command line
python manage.py shell
>>> from lawfirm.models import Question, QACategory
>>> cat = QACategory.objects.first()
>>> q = Question.objects.create(
...     title="سوال جدید",
...     slug="so-al-jadid",
...     content="محتوا سوال",
...     asker_name="نام پرسنده",
...     asker_email="email@example.com",
...     category=cat,
...     is_published=True
... )
```

### Viewing Database Content
```bash
python manage.py shell
>>> from lawfirm.models import Question
>>> Question.objects.count()  # Count questions
29
>>> Question.objects.values('title')[:5]  # Show first 5 titles
```

### Troubleshooting
```bash
# Check server logs
tail -f /tmp/django_server.log

# Run diagnostics
./check_and_fix.sh check

# Check database
python manage.py dbshell

# Reset database
python manage.py flush  # Warning: deletes all data!
```

## 📞 Support

- **Documentation**: See SETUP_GUIDE.md
- **Issues**: Review COMPLETION_SUMMARY.md
- **Logs**: /tmp/django_server.log
- **Admin**: http://127.0.0.1:8000/admin

## 🎓 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Schema.org Markup](https://schema.org/)
- [Farsi/Persian Web Best Practices](https://fa.wikipedia.org/)
- [SEO Best Practices](https://moz.com/beginners-guide-to-seo)

---

**Project**: Dadgan Legal Institution Website
**Framework**: Django 4.2+
**Language**: Python 3.8+
**Database**: SQLite (dev) / PostgreSQL (production)
**Last Updated**: December 2, 2025
**Status**: Production Ready ✅
