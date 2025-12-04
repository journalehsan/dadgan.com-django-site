from django.core.management.base import BaseCommand
from lawfirm.models import ConsultationType, Category, QACategory


class Command(BaseCommand):
    help = 'Populate initial data for consultation types and categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating initial data...\n')

        # Create Consultation Types
        consultation_types = [
            {
                'name': 'مشاوره تلفنی',
                'price': 150000,
                'duration': 30,
                'description': 'مشاوره تلفنی 30 دقیقه‌ای با وکیل پایه یک',
                'is_active': True
            },
            {
                'name': 'مشاوره حضوری',
                'price': 300000,
                'duration': 60,
                'description': 'مشاوره حضوری یک ساعته در دفتر',
                'is_active': True
            },
            {
                'name': 'مشاوره آنلاین (ویدیو)',
                'price': 200000,
                'duration': 45,
                'description': 'مشاوره آنلاین 45 دقیقه‌ای از طریق ویدیو کال',
                'is_active': True
            },
        ]

        for ct_data in consultation_types:
            ct, created = ConsultationType.objects.get_or_create(
                name=ct_data['name'],
                defaults=ct_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {ct.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Already exists: {ct.name}'))

        # Create Blog Categories
        blog_categories = [
            {'name': 'حقوق خانواده', 'slug': 'family-law', 'description': 'مقالات مربوط به حقوق خانواده، طلاق، نفقه و ...'},
            {'name': 'حقوق کیفری', 'slug': 'criminal-law', 'description': 'مقالات مربوط به جرائم، دفاع و ...'},
            {'name': 'حقوق ملکی', 'slug': 'property-law', 'description': 'مقالات مربوط به املاک و مستغلات'},
            {'name': 'حقوق تجاری', 'slug': 'commercial-law', 'description': 'مقالات مربوط به شرکت‌ها و قراردادهای تجاری'},
        ]

        for cat_data in blog_categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created category: {cat.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Category already exists: {cat.name}'))

        # Create QA Categories
        qa_categories = [
            {'name': 'حقوق خانواده', 'slug': 'family', 'description': 'سوالات مربوط به طلاق، نفقه، حضانت و ...'},
            {'name': 'حقوق کیفری', 'slug': 'criminal', 'description': 'سوالات مربوط به جرائم و دفاع'},
            {'name': 'حقوق ملکی', 'slug': 'property', 'description': 'سوالات مربوط به املاک'},
            {'name': 'حقوق تجاری', 'slug': 'commercial', 'description': 'سوالات مربوط به شرکت‌ها'},
            {'name': 'سایر موارد', 'slug': 'other', 'description': 'سایر سوالات حقوقی'},
        ]

        for qa_data in qa_categories:
            qa, created = QACategory.objects.get_or_create(
                slug=qa_data['slug'],
                defaults=qa_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created QA category: {qa.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'- QA category already exists: {qa.name}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Initial data population completed!'))
