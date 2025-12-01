# Dadgan Legal Institution - Django Site

A modern Django-based website for Dadgan Legal Institution (موسسه حقوقی دادگان) with comprehensive SEO optimization, Q&A functionality, and blog management.

## 🎯 Features

### Core Functionality
- **Blog Management**: Write and publish legal articles
- **Q&A System**: Questions and answers about legal matters
- **Consultation Booking**: Book legal consultations
- **Contact Management**: Collect inquiries and feedback
- **Admin Dashboard**: Django admin interface for managing content

### SEO Optimization
- **Meta Tags**: Custom SEO title, description, and keywords for every page
- **Schema.org Markup**: Structured data for better search engine understanding
  - FAQ Schema for Q&A pages
  - Article Schema for blog posts
  - Organization Schema
  - Breadcrumb Schema
- **URL Slugs**: SEO-friendly URLs in Farsi
- **Farsi Content Support**: Full RTL support for Persian/Farsi content
- **Keyword Targeting**: Optimized for "موسسه حقوقی" (Legal Institution) keyword

### Data Migration
- Imported 29 Q&A questions from legacy Laravel/WordPress database
- Automatic data extraction and transformation from MySQL dumps
- Preserved original content and metadata

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- uv (Python package manager)
- SQLite3
- Pillow for image handling

### Quick Start

1. **Setup Environment**
   ```bash
   ./manage_site.sh setup
   ```

2. **Start Server**
   ```bash
   ./manage_site.sh start
   ```

3. **Access Admin Panel**
   - URL: `http://127.0.0.1:8000/admin`
   - Username: `admin`
   - Password: `admin123`

### Available Commands

```bash
# Setup Python environment
./manage_site.sh setup

# Start Django development server
./manage_site.sh start

# Stop running server
./manage_site.sh stop

# Restart server
./manage_site.sh restart

# Check server status
./manage_site.sh status

# Check and fix issues
./check_and_fix.sh check
./check_and_fix.sh fix
./check_and_fix.sh full
```

## 📊 Models

### BlogPost
- Title, slug, content, excerpt
- Author, category, featured status
- Image field for blog thumbnails
- View counter
- **SEO Fields**: seo_title, seo_description, seo_keywords

### Question
- Title, content, category
- Asker details (name, email)
- Published/answered status
- View and vote counters
- Related answers
- **SEO Fields**: seo_title, seo_description, seo_keywords

### Answer
- Content, author details
- Best answer marking
- Vote system
- Published status

### Category & QACategory
- Hierarchical categorization
- Slugs for SEO-friendly URLs

### ConsultationRequest
- Full consultation booking system
- Multiple field types
- Status tracking

## 🔍 SEO Features

### Automatic SEO Generation
Models include methods for generating SEO metadata:

```python
# Get optimized SEO title (fallback to title if not set)
question.get_seo_title()

# Get optimized SEO description (auto-generate from content)
question.get_seo_description()

# Get SEO keywords with automatic additions
question.get_seo_keywords()
```

### Template Tags
```django
{% load seo_tags %}

{# Display SEO meta tags #}
<meta name="title" content="{{ seo_title }}">
<meta name="description" content="{{ seo_description }}">
<meta name="keywords" content="{{ seo_keywords }}">

{# Render structured data #}
{% question_schema question %}
{% article_schema blog %}
{% organization_schema %}
{% breadcrumb_schema breadcrumbs %}
```

### Structured Data (Schema.org)
- FAQ pages include JSON-LD schema
- Article pages include detailed article schema
- Organization info in footer
- Breadcrumb navigation schema

## 📥 Data Import

### Importing Q&A Data

The site includes a management command to import Q&A data from the legacy Laravel/WordPress system:

```bash
python manage.py import_qa_data
```

Options:
```bash
# Import with custom file
python manage.py import_qa_data --qa-file path/to/qa_posts.json

# Skip existing questions
python manage.py import_qa_data --skip-existing
```

### Extracting from Remote Server

To extract data from the remote Laravel/WordPress server:

```bash
./migrate_from_laravel.sh full
```

This will:
1. Connect to the remote server via SSH
2. Export both WordPress and FAQ databases
3. Create backup files in `laravel_backup/`
4. Analyze database structure

### Analysis & Extraction

```bash
# Extract and analyze data
python3 extract_data_final.py

# Output in: data_extraction/qa_posts.json
```

## 📁 Project Structure

```
dadgan_project/
├── settings.py          # Django settings
├── urls.py              # URL routing
└── wsgi.py              # Production WSGI config

lawfirm/
├── models.py            # Database models with SEO fields
├── views.py             # View logic
├── forms.py             # Django forms
├── seo.py               # SEO utilities and schema generation
├── urls.py              # App URL patterns
├── admin.py             # Admin interface
├── management/
│   └── commands/
│       └── import_qa_data.py    # Data import command
├── templatetags/
│   └── seo_tags.py      # Custom template tags
└── migrations/          # Database migrations

templates/
├── base.html            # Base template with SEO meta tags
└── lawfirm/
    ├── home.html        # Homepage
    ├── blog_list.html   # Blog listing
    ├── blog_detail.html # Blog detail with article schema
    ├── qa_list.html     # Q&A listing
    └── qa_detail.html   # Q&A detail with FAQ schema

static/
├── css/                 # Stylesheets
├── js/                  # JavaScript
└── images/              # Image assets

laravel_backup/         # Exported data from remote server
├── c1dadgan.sql         # WordPress database dump
└── c1faq.sql            # FAQ database dump

data_extraction/        # Extracted data for import
├── qa_posts.json        # Extracted Q&A posts
└── wordpress_posts.json # Extracted blog posts
```

## 🚀 Production Deployment

### WSGI Server Setup
```bash
gunicorn dadgan_project.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables
Create `.env` file:
```
DEBUG=False
ALLOWED_HOSTS=dadgan.com,www.dadgan.com
DATABASE_URL=postgresql://user:password@localhost/dadgan
SECRET_KEY=your-secret-key-here
```

### Database
For production, use PostgreSQL:
```bash
pip install psycopg2-binary
```

## 🔧 Maintenance

### Database Backups
```bash
python manage.py dumpdata > backup_$(date +%Y%m%d).json
```

### Static Files Collection
```bash
python manage.py collectstatic
```

## 📝 Content Guidelines

### Blog Posts
- Use clear, SEO-friendly titles
- Include meta description (160 chars max)
- Add relevant keywords
- Include feature image
- Write comprehensive content
- Internal linking to related posts

### Q&A Posts
- Clear, specific questions
- Detailed answers
- Categorize properly
- Add SEO keywords (optional)
- Mark best answers
- Encourage community participation

## 🌐 Localization

The site is fully optimized for Persian/Farsi:
- Right-to-left (RTL) text direction
- Persian numbering support
- Farsi month names
- RTL admin interface
- Unicode slug support

## 📊 SEO Keywords

Target Keywords:
- موسسه حقوقی دادگان
- مشاوره حقوقی
- وکیل تهران
- حقوق خانواده
- حقوق تجاری
- حقوق کیفری
- مشاوره حقوقی رایگان

## 🔐 Security

- CSRF protection enabled
- SQL injection prevention via ORM
- XSS protection in templates
- HTTPS recommended for production
- Admin authentication required
- Content validation on forms

## 📞 Support & Contribution

For issues, improvements, or questions:
- Email: journalehsan@gmail.com
- Website: https://dadgan.com

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Django framework
- Bootstrap 5 for styling
- PostgreSQL for production database
- All contributors and users

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
**Status**: Active Development
