from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lawfirm.models import BlogPost, Category
from django.utils.text import slugify
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate blog posts with law firm content in Farsi for SEO improvement'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )

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
