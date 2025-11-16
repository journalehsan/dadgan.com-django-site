from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from lawfirm.models import *


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Get admin user
        admin_user = User.objects.get(username='admin')
        
        # Create Categories
        blog_categories = [
            ('حقوق خانواده', 'family-law'),
            ('حقوق تجاری', 'commercial-law'),
            ('حقوق کیفری', 'criminal-law'),
            ('حقوق مدنی', 'civil-law'),
        ]
        
        for name, slug in blog_categories:
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': f'مقالات مربوط به {name}'}
            )
            if created:
                self.stdout.write(f'Created category: {name}')

        # Create QA Categories
        qa_categories = [
            ('حقوق خانواده', 'family-law'),
            ('حقوق تجاری', 'commercial-law'),
            ('حقوق کیفری', 'criminal-law'),
            ('حقوق عمومی', 'public-law'),
        ]
        
        for name, slug in qa_categories:
            qa_category, created = QACategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': f'سوالات مربوط به {name}'}
            )
            if created:
                self.stdout.write(f'Created QA category: {name}')

        # Create Blog Posts
        blog_posts = [
            {
                'title': 'راهنمای کامل طلاق توافقی در ایران',
                'category': 'family-law',
                'excerpt': 'شرایط، مراحل و مدارک لازم برای طلاق توافقی و نحوه انجام آن در دادگاه‌های خانواده',
                'content': '''طلاق توافقی یکی از انواع طلاق است که با توافق زوجین انجام می‌شود. در این نوع طلاق، زوجین با توافق کامل نسبت به تمامی شرایط طلاق از جمله نفقه، حضانت فرزندان و تقسیم اموال، درخواست طلاق می‌دهند.

**شرایط طلاق توافقی:**

1. توافق کامل زوجین
2. تکمیل فرم‌های مربوطه
3. ارائه مدارک هویتی
4. گذراندن دوره مشاوره خانواده

**مراحل انجام:**

1. مراجعه به دفتر طلاق
2. تکمیل فرم‌ها و ارائه مدارک
3. شرکت در جلسات مشاوره
4. صدور حکم طلاق

این روند معمولاً بین 2 تا 4 هفته طول می‌کشد و هزینه‌های آن به مراتب کمتر از طلاق غیرتوافقی است.'''
            },
            {
                'title': 'نحوه تنظیم قرارداد خرید و فروش ملک',
                'category': 'commercial-law',
                'excerpt': 'نکات مهم و ضروری در تنظیم قرارداد خرید و فروش املاک و راهنمای کامل',
                'content': '''قرارداد خرید و فروش ملک یکی از مهم‌ترین اسناد حقوقی است که باید با دقت و توجه به تمامی نکات قانونی تنظیم شود.

**عناصر اصلی قرارداد:**

1. مشخصات کامل طرفین
2. مشخصات دقیق ملک
3. قیمت و نحوه پرداخت
4. تعیین مسئولیت‌های طرفین

**نکات مهم:**

- بررسی سند و اسناد مالکیت
- وضعیت قانونی ملک
- عدم وجود بدهی و محدودیت
- بیمه و انتقال کنتورها

**مراحل عقد قرارداد:**

1. بررسی اولیه ملک
2. تنظیم پیش‌قرارداد
3. انجام استعلامات لازم
4. عقد قرارداد نهایی
5. انتقال رسمی

توصیه می‌شود حتماً از خدمات وکیل مجرب استفاده کنید.'''
            },
            {
                'title': 'حقوق متهم در دادرسی کیفری',
                'category': 'criminal-law',
                'excerpt': 'شناخت حقوق اساسی متهم در فرآیند دادرسی کیفری و نحوه دفاع از حقوق خود',
                'content': '''متهم در دادرسی کیفری دارای حقوق اساسی است که قانون آن‌ها را به رسمیت شناخته است.

**حقوق اساسی متهم:**

1. حق داشتن وکیل
2. حق سکوت و عدم اعتراف
3. حق اطلاع از اتهام
4. حق دفاع و ارائه دلیل

**مراحل دادرسی:**

1. مرحله تحقیقات مقدماتی
2. صدور کیفرخواست
3. رسیدگی در دادگاه
4. صدور حکم

**نکات مهم:**

- هرگز بدون وکیل اظهارات ندهید
- از حق سکوت استفاده کنید
- مدارک دفاعی خود را آماده کنید
- در موعدهای تعیین شده حاضر شوید

در صورت بازداشت، حق تماس با وکیل و خانواده را دارید.'''
            }
        ]

        for post_data in blog_posts:
            category = Category.objects.get(slug=post_data['category'])
            blog_post, created = BlogPost.objects.get_or_create(
                slug=slugify(post_data['title'], allow_unicode=True),
                defaults={
                    'title': post_data['title'],
                    'author': admin_user,
                    'category': category,
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'published': True,
                    'featured': True,
                    'views': 150 + len(post_data['title']) * 2
                }
            )
            if created:
                self.stdout.write(f'Created blog post: {post_data["title"]}')

        # Create Questions and Answers
        questions_data = [
            {
                'title': 'آیا می‌توانم بدون وکیل در دادگاه حاضر شوم؟',
                'category': 'public-law',
                'content': 'سلام، می‌خواهم بدانم آیا برای حضور در دادگاه الزاماً باید وکیل داشته باشم یا می‌توانم خودم دفاع کنم؟',
                'asker_name': 'علی محمدی',
                'asker_email': 'ali@example.com',
                'answers': [
                    {
                        'content': 'بله، در بسیاری از دعاوی می‌توانید بدون وکیل حاضر شوید اما در برخی موارد خاص مثل دادگاه‌های کیفری درجه یک، وجود وکیل الزامی است. توصیه می‌شود برای پیچیدگی‌های قانونی از وکیل مشاوره بگیرید.',
                        'answerer_name': 'وکیل دادگان',
                        'answerer_title': 'وکیل پایه یک دادگستری',
                        'votes': 15,
                        'is_best_answer': True
                    }
                ]
            },
            {
                'title': 'مدت زمان طلاق توافقی چقدر است؟',
                'category': 'family-law',
                'content': 'من و همسرم تصمیم به طلاق توافقی گرفته‌ایم. می‌خواهم بدانم این روند چقدر طول می‌کشد؟',
                'asker_name': 'مریم احمدی',
                'asker_email': 'maryam@example.com',
                'answers': [
                    {
                        'content': 'طلاق توافقی معمولاً بین ۲ تا ۴ هفته طول می‌کشد، بسته به شرایط و تکمیل مدارک. باید دوره مشاوره ۶ جلسه‌ای را طی کنید و سپس حکم صادر می‌شود.',
                        'answerer_name': 'وکیل دادگان',
                        'answerer_title': 'وکیل پایه یک دادگستری',
                        'votes': 12,
                        'is_best_answer': True
                    },
                    {
                        'content': 'دقیقاً، و هزینه‌ها نیز به مراتب کمتر از طلاق غیرتوافقی است. مهم این است که توافق کاملی بین طرفین وجود داشته باشد.',
                        'answerer_name': 'مشاور حقوقی',
                        'answerer_title': 'کارشناس حقوق خانواده',
                        'votes': 8,
                        'is_best_answer': False
                    }
                ]
            },
            {
                'title': 'هزینه تنظیم قرارداد خرید ملک چقدر است؟',
                'category': 'commercial-law',
                'content': 'قصد خرید آپارتمان دارم و می‌خواهم بدانم هزینه وکیل برای تنظیم قرارداد چقدر است؟',
                'asker_name': 'رضا کریمی',
                'asker_email': 'reza@example.com',
                'answers': [
                    {
                        'content': 'هزینه تنظیم قرارداد بستگی به ارزش ملک دارد و معمولاً بین ۰.۵ تا ۲ درصد ارزش ملک است. برای ملک ۵ میلیارد تومانی، حدود ۲۵ تا ۱۰۰ میلیون تومان هزینه دارد.',
                        'answerer_name': 'وکیل دادگان',
                        'answerer_title': 'وکیل پایه یک دادگستری',
                        'votes': 3,
                        'is_best_answer': True
                    }
                ]
            }
        ]

        for q_data in questions_data:
            qa_category = QACategory.objects.get(slug=q_data['category'])
            question, created = Question.objects.get_or_create(
                slug=slugify(q_data['title'], allow_unicode=True),
                defaults={
                    'title': q_data['title'],
                    'content': q_data['content'],
                    'asker_name': q_data['asker_name'],
                    'asker_email': q_data['asker_email'],
                    'category': qa_category,
                    'is_published': True,
                    'views': 245 + len(q_data['title']),
                    'votes': 15
                }
            )
            
            if created:
                self.stdout.write(f'Created question: {q_data["title"]}')
                
                # Create answers
                for a_data in q_data['answers']:
                    answer = Answer.objects.create(
                        question=question,
                        content=a_data['content'],
                        answerer_name=a_data['answerer_name'],
                        answerer_title=a_data['answerer_title'],
                        votes=a_data['votes'],
                        is_best_answer=a_data['is_best_answer'],
                        is_published=True
                    )

        # Create Consultation Types
        consultation_types = [
            {
                'name': 'مشاوره تلفنی',
                'price': 150000,
                'duration': 30,
                'description': 'مشاوره فوری ۳۰ دقیقه‌ای از طریق تماس تلفنی'
            },
            {
                'name': 'مشاوره حضوری',
                'price': 300000,
                'duration': 60,
                'description': 'مشاوره دقیق و تخصصی به صورت حضوری در دفتر'
            }
        ]

        for ct_data in consultation_types:
            consultation_type, created = ConsultationType.objects.get_or_create(
                name=ct_data['name'],
                defaults=ct_data
            )
            if created:
                self.stdout.write(f'Created consultation type: {ct_data["name"]}')

        # Create Testimonials
        testimonials = [
            {
                'name': 'خانم رضایی',
                'title': 'مشتری',
                'content': 'مشاوره بسیار عالی و دقیق. موضوع پرونده‌ام خیلی سریع پیش رفت و نتیجه فوق‌العاده‌ای گرفتم.',
                'rating': 5
            },
            {
                'name': 'آقای محمدی',
                'title': 'مشتری',
                'content': 'از نظر تعهد و حرفه‌ای‌گری بی‌نظیر هستند. کیفیت خدمات بسیار بالا و قابل اعتماد.',
                'rating': 5
            },
            {
                'name': 'آقای علیپور',
                'title': 'مشتری',
                'content': 'بهترین مؤسسه‌ای که تاکنون تجربه کرده‌ام. خدمات جامع و مشاوره دقیق.',
                'rating': 5
            }
        ]

        for t_data in testimonials:
            testimonial, created = Testimonial.objects.get_or_create(
                name=t_data['name'],
                defaults=t_data
            )
            if created:
                self.stdout.write(f'Created testimonial: {t_data["name"]}')

        # Create Site Settings
        site_settings, created = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                'site_title': 'مؤسسه حقوقی دادگان',
                'site_description': 'ارائه‌دهنده خدمات وکالت، مشاوره حقوقی، تنظیم قراردادها و دفاع حرفه‌ای توسط وکلای پایه یک دادگستری.',
                'phone': '09129413828',
                'email': 'info@dadgan.ir',
                'address': 'جهان کودک، جنب خیابان ثانعی، برج امیر پرویز',
                'consultation_count': 1400,
                'success_cases': 950,
                'contracts_count': 500,
                'experience_years': 12
            }
        )
        if created:
            self.stdout.write('Created site settings')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))