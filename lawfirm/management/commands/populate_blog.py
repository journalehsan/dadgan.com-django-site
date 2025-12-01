from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lawfirm.models import BlogPost, Category
from django.utils.text import slugify
from datetime import datetime
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
                
                # Create slug
                slug = post_data.get('post_name') or slugify(title[:100], allow_unicode=True)
                
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


        blog_data = [
            {
                'title': 'مشاوره حقوقی آنلاین برای مسائل خانوادگی',
                'category': 'مشاوره حقوقی خانوادگی',
                'content': '''موسسه حقوقی ما با تجربه بیش از ۲۰ سال در زمینه مسائل خانوادگی، به شما کمک می‌کند.

مسائلی مثل:
• طلاق و تقسیم اموال
• حضانت فرزندان
• نفقه و نفقه دائمی
• فسخ عقد ازدواج

تیم متخصص ما آماده است تا بهترین راهکار را برای شرایط خاص شما پیدا کند.

تماس بگیرید برای یک جلسه مشاوره رایگان امروز!''',
                'seo_title': 'مشاوره حقوقی آنلاین مسائل خانوادگی | موسسه حقوقی دادگان',
                'seo_description': 'مشاوره حقوقی تخصصی در مسائل خانوادگی، طلاق و حضانت از بهترین وکلای خانوادگی',
                'seo_keywords': 'مشاوره حقوقی، وکیل خانوادگی، طلاق، حضانت فرزندان',
            },
            {
                'title': 'حقوق کار و بیمه اجتماعی',
                'category': 'حقوق کار',
                'content': '''شرکت های بزرگ و کارفرمایان باید از حقوق کارگران محافظت کنند.

ما در زمینه‌های زیر کمک می‌کنیم:
• قرارداد کار
• غرامت و جبران خسارت
• بیمه اجتماعی
• اخراج غیرقانونی
• مسائل حقوقی کارگاه و کارخانه

تیم وکلای کار ما از حقوق کارگران و کارفرمایان دفاع می‌کند.''',
                'seo_title': 'وکیل حقوق کار و بیمه اجتماعی | موسسه حقوقی دادگان',
                'seo_description': 'خدمات حقوقی کار، قرارداد کار، غرامت و مسائل بیمه اجتماعی',
                'seo_keywords': 'حقوق کار، وکیل کار، قرارداد کار، بیمه اجتماعی',
            },
            {
                'title': 'حقوق تجاری و ثبت شرکت',
                'category': 'حقوق تجاری',
                'content': '''آغاز یک کسب و کار جدید نیازمند مشاوره حقوقی است.

خدمات تجاری ما شامل:
• ثبت شرکت
• قراردادهای تجاری
• مسائل شراکت
• بدهی و دیون تجاری
• حل اختلافات تجاری

متخصصین ما با تجربه در حوزه حقوق تجاری و بازرگانی، راهنمایی مناسبی انجام می‌دهند.''',
                'seo_title': 'وکیل حقوق تجاری و ثبت شرکت | موسسه حقوقی دادگان',
                'seo_description': 'خدمات حقوقی تجاری، ثبت شرکت، قرارداد تجاری و حل اختلافات',
                'seo_keywords': 'حقوق تجاری، ثبت شرکت، قرارداد تجاری، حقوق بازرگانی',
            },
            {
                'title': 'مسائل ملکی و معاملات رسمی',
                'category': 'حقوق ملکی',
                'content': '''خریدوفروش ملک و معاملات رسمی نیازمند تحقیق حقوقی دقیق است.

ما در موارد زیر خدمت می‌دهیم:
• خریدوفروش ملک
• اجاره و استیجار
• رهن و وام ملکی
• تقسیم ارث
• معاملات رسمی

وکلای ملکی ما از حقوق شما در تمام مراحل معاملات حفاظت می‌کنند.''',
                'seo_title': 'وکیل ملکی و معاملات رسمی | موسسه حقوقی دادگان',
                'seo_description': 'خدمات حقوقی ملکی، خریدوفروش ملک و معاملات رسمی',
                'seo_keywords': 'وکیل ملکی، خریدوفروش ملک، معاملات رسمی، رهن',
            },
            {
                'title': 'دفاع در دعاوی مدنی و کیفری',
                'category': 'دفاع قانونی',
                'content': '''اگر با دعوای مدنی یا کیفری روبه‌رو هستید، نیاز به دفاع قوی دارید.

تجربه ما در:
• دفاع مجرمانه
• دعاوی مدنی
• دعاوی خصوصی
• شکایات و تظلمات
• دفاع در دادگاه‌های مختلف

تیم وکلای ما با تجربه گسترده در دفاع، حقوق شما را در دادگاه‌های مختلف حفاظت می‌کند.''',
                'seo_title': 'وکیل دفاع مدنی و کیفری | موسسه حقوقی دادگان',
                'seo_description': 'خدمات حقوقی دفاع در دعاوی مدنی و کیفری، وکیل دادگاه',
                'seo_keywords': 'وکیل دفاع، دعوای مدنی، دعوای کیفری, وکیل دادگاه',
            },
            {
                'title': 'مشاوره حقوقی برای افراد و خانواده‌ها',
                'category': 'مشاوره عمومی',
                'content': '''هر فردی می‌تواند با مسائل حقوقی مختلفی روبه‌رو شود.

موسسه حقوقی ما برای:
• افراد عادی
• خانواده‌ها
• کارگران
• کارآفرینان

مشاوره حقوقی جامع و متخصص ارائه می‌دهد.

ما معتقدیم که هر کسی حق دسترسی به مشاوره حقوقی کیفی را دارد.''',
                'seo_title': 'مشاوره حقوقی برای افراد و خانواده‌ها | موسسه حقوقی دادگان',
                'seo_description': 'مشاوره حقوقی عمومی برای افراد، خانواده‌ها و کارآفرینان',
                'seo_keywords': 'مشاوره حقوقی عمومی، وکیل حقوق عمومی، مشاوره حقوقی رایگان',
            },
        ]

        # Create blog posts
        created_count = 0
        for i, post_data in enumerate(blog_data):
            # Generate slug from Farsi title
            slug = slugify(post_data['title'], allow_unicode=True)
            
            # Create or get category
            category, _ = Category.objects.get_or_create(
                name=post_data['category'],
                defaults={'slug': slugify(post_data['category'], allow_unicode=True)}
            )
            
            # Create or update blog post
            blog_post, created = BlogPost.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': post_data['title'],
                    'author': admin_user,
                    'category': category,
                    'excerpt': post_data['content'][:300],
                    'content': post_data['content'],
                    'seo_title': post_data['seo_title'],
                    'seo_description': post_data['seo_description'],
                    'seo_keywords': post_data['seo_keywords'],
                    'published': True,
                    'featured': i < 3,  # First 3 are featured
                    'views': 0,
                    'created_at': datetime.now() - timedelta(days=len(blog_data) - i),
                    'updated_at': datetime.now() - timedelta(days=len(blog_data) - i),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {post_data["title"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated: {post_data["title"]}')
                )

        total_posts = BlogPost.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Blog population complete! Created: {created_count}, Total posts: {total_posts}'
            )
        )
