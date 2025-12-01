from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lawfirm.models import BlogPost, Category
from django.utils.text import slugify
from datetime import datetime
from urllib.parse import unquote
import json


class Command(BaseCommand):
    help = 'Import blog posts from extracted WordPress data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data_extraction/wordpress_posts.json',
            help='Path to WordPress posts JSON file'
        )

    def handle(self, *args, **options):
        json_file = options['file']
        
        self.stdout.write("=" * 60)
        self.stdout.write("Importing WordPress Blog Posts")
        self.stdout.write("=" * 60)
        
        # Load JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {json_file}"))
            self.stdout.write("Please run: python3 extract_simple.py first")
            return
        
        self.stdout.write(f"Found {len(posts)} posts to import")
        
        # Get or create admin user
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@dadgan.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Get or create default category
        default_category, _ = Category.objects.get_or_create(
            slug='general',
            defaults={
                'name': 'عمومی',
                'description': 'مقالات عمومی حقوقی'
            }
        )
        
        imported = 0
        skipped = 0
        
        for post_data in posts:
            try:
                post_id = post_data.get('ID')
                title = post_data.get('post_title', '').strip()
                
                if not title:
                    self.stdout.write(f"Skipping post {post_id}: No title")
                    skipped += 1
                    continue
                
                # Create slug - decode URL-encoded post_name first
                post_name = post_data.get('post_name')
                if post_name:
                    # URL-decode the WordPress post_name (it's URL-encoded)
                    slug = unquote(post_name)
                else:
                    slug = slugify(title[:100], allow_unicode=True)
                
                # Clean slug - remove characters not allowed by Django's slug converter
                # Django slug allows: letters, numbers, hyphens, underscores
                # Remove Persian comma and other punctuation
                slug = slug.replace('،', '-').replace(',', '-')  # Replace commas with hyphens
                
                # Ensure unique slug
                original_slug = slug
                counter = 1
                while BlogPost.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                # Get content and excerpt
                content = post_data.get('post_content', '')
                excerpt = post_data.get('post_excerpt', '')
                
                if not excerpt and content:
                    # Create excerpt from content - remove HTML tags
                    import re
                    clean_content = re.sub(r'<[^>]+>', '', content)
                    excerpt = clean_content[:297] + '...' if len(clean_content) > 300 else clean_content
                
                # Parse dates
                post_date = post_data.get('post_date')
                try:
                    created_at = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S') if post_date else datetime.now()
                except:
                    created_at = datetime.now()
                
                # Create or update blog post
                blog_post, created = BlogPost.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'title': title,
                        'author': admin_user,
                        'category': default_category,
                        'excerpt': excerpt[:300],
                        'content': content,
                        'published': True,
                        'featured': imported < 3,  # First 3 as featured
                        'views': 0,
                        'created_at': created_at,
                        'seo_title': title[:60],
                        'seo_description': excerpt[:160] if excerpt else '',
                        'seo_keywords': 'موسسه حقوقی, مشاوره حقوقی, وکیل, دادگان'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Imported: {title[:60]}"))
                    imported += 1
                else:
                    self.stdout.write(self.style.WARNING(f"⟳ Updated: {title[:60]}"))
                    imported += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error importing post {post_data.get('ID')}: {e}"))
                skipped += 1
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"✓ Import Complete!"))
        self.stdout.write(f"  Imported/Updated: {imported}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Total in database: {BlogPost.objects.count()}")
        self.stdout.write("=" * 60)
