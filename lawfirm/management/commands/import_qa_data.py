from django.core.management.base import BaseCommand
from django.utils.text import slugify
from lawfirm.models import Question, QACategory, Answer
from datetime import datetime
import json
import os


class Command(BaseCommand):
    help = "Import Q&A posts from extracted Laravel database"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data_extraction/qa_posts.json',
            help='Path to extracted Q&A JSON file'
        )

    def handle(self, *args, **options):
        json_file = options['file']
        
        self.stdout.write("=" * 60)
        self.stdout.write("Importing Q&A Posts")
        self.stdout.write("=" * 60)

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"File not found: {json_file}"))
            self.stdout.write("Please run: python3 extract_simple.py first")
            return

        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)

        self.stdout.write(f"Found {len(posts)} Q&A posts to import")

        # Get or create default category
        category, created = QACategory.objects.get_or_create(
            name="سوالات و پاسخ‌ها",
            defaults={
                'slug': 'qa-general',
                'description': 'سوالات و پاسخ‌های عمومی درباره موضوعات حقوقی'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))

        # Get or create admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                'admin',
                'admin@dadgan.com',
                'admin123'
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin user"))

        # Group posts by parent (question) ID
        questions_dict = {}
        answers_dict = {}

        for post in posts:
            post_id = post.get('post_id')
            parent_id = post.get('parrent', post.get('parent', '0'))
            post_type = post.get('type', 'Q')

            if post_type == 'Q':
                questions_dict[post_id] = post
            else:  # Answer
                if parent_id not in answers_dict:
                    answers_dict[parent_id] = []
                answers_dict[parent_id].append(post)

        # Import questions
        imported_count = 0
        skipped_count = 0

        for q_id, q_post in questions_dict.items():
            title = q_post.get('title', '').strip()
            if not title:
                self.stdout.write(self.style.WARNING(f"Skipping question with no title (ID: {q_id})"))
                continue

            # Create slug
            slug = slugify(title[:50], allow_unicode=True)
            
            # Check if already exists
            if skip_existing and Question.objects.filter(slug=slug).exists():
                skipped_count += 1
                continue

            # Handle slug uniqueness
            base_slug = slug
            counter = 1
            while Question.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            try:
                question = Question.objects.create(
                    title=title,
                    slug=slug,
                    content=q_post.get('content', ''),
                    asker_name='پرسنده',
                    asker_email='info@dadgan.com',
                    category=category,
                    views=int(q_post.get('views', 0)),
                    is_published=True,
                    is_answered=q_id in answers_dict and len(answers_dict[q_id]) > 0
                )

                # Import answers
                if q_id in answers_dict:
                    for a_post in answers_dict[q_id]:
                        answer_content = a_post.get('content', '')
                        if answer_content:
                            Answer.objects.create(
                                question=question,
                                content=answer_content,
                                answerer_name='موسسه حقوقی دادگان',
                                answerer_title='متخصص حقوق',
                                is_published=True,
                                is_best_answer=False,
                                votes=0
                            )

                imported_count += 1
                if imported_count % 10 == 0:
                    self.stdout.write(f"  Imported {imported_count} questions...")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing question {q_id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n✓ Import complete!"))
        self.stdout.write(self.style.SUCCESS(f"  Imported: {imported_count} questions"))
        self.stdout.write(self.style.SUCCESS(f"  Skipped: {skipped_count} questions"))
