# Dadgan Law Firm - Django Website

A professional Persian law firm website built with Django, featuring a modern responsive design, blog system, Q&A platform, and consultation booking.

## 🚀 Features

- **Modern Persian/RTL Design**: Clean and professional interface with Vazirmatn font
- **Blog System**: Complete blog with categories, tags, and content management
- **Q&A Platform**: Stack Overflow-like Q&A system for legal questions
- **Consultation Booking**: Online consultation request system
- **Contact Forms**: Multiple contact forms with validation
- **Admin Panel**: Full Django admin interface for content management
- **Responsive Design**: Mobile-first responsive design with dark mode support
- **SEO Friendly**: Optimized URLs and meta tags

## 🛠️ Technologies

- **Backend**: Django 5.2.8
- **Database**: SQLite (production-ready for PostgreSQL)
- **Frontend**: TailwindCSS, JavaScript
- **Typography**: Vazirmatn Persian font
- **Icons**: Unicode emojis and symbols

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/dadgan.com-django-site.git
   cd dadgan.com-django-site
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional):**
   ```bash
   python manage.py shell
   # Run the sample data creation script
   ```

7. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## 🏗️ Project Structure

```
dadgan_lawfirm/
├── dadgan_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── lawfirm/                 # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # URL patterns
│   ├── admin.py             # Admin configuration
│   └── forms.py             # Django forms
├── templates/               # HTML templates
│   ├── base.html
│   └── lawfirm/
├── static/                  # Static assets
│   ├── css/
│   ├── js/
│   └── images/
└── media/                   # User uploads
```

## 📊 Database Models

- **BlogPost**: Blog articles with categories and tags
- **Question/Answer**: Q&A system with voting
- **ConsultationRequest**: Online consultation bookings
- **ContactMessage**: Contact form submissions
- **Testimonial**: Client testimonials
- **SiteSettings**: Dynamic site configuration

## 🎨 Design Features

- **Persian/RTL Support**: Complete right-to-left text support
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Layout**: Mobile-first design approach
- **Animation Effects**: Smooth transitions and hover effects
- **Color-coded Categories**: Dynamic color assignment for different content types

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@localhost/dbname
```

### Admin Panel
Access the admin panel at `/admin/` with the superuser credentials.

**Default admin credentials (if using sample data):**
- Username: `admin`
- Password: `admin123`

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Set up PostgreSQL database
4. Configure static files serving
5. Set up media files handling

### Sample Deployment Commands
```bash
python manage.py collectstatic
python manage.py migrate
gunicorn dadgan_project.wsgi:application
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created with ❤️ for Dadgan Law Firm

## 📞 Support

For support and questions, please contact through the website's contact form or open an issue on GitHub.