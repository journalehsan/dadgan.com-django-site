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
            slug='general',
            defaults={
                'name': 'سوالات عمومی',
                'description': 'سوالات و پاسخ‌های عمومی حقوقی'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))
        
        # Separate questions and answers
        questions_data = [p for p in posts if p.get('type') == 'Q']
        answers_data = [p for p in posts if p.get('type') == 'A']
        
        self.stdout.write(f"  Questions: {len(questions_data)}")
        self.stdout.write(f"  Answers: {len(answers_data)}")
        
        # First import all questions
        question_map = {}  # Map old post_id to new Question object
        imported_q = 0
        skipped_q = 0
        
        self.stdout.write("\nImporting Questions...")
        for q_data in questions_data:
            try:
                post_id = q_data.get('post_id')
                title = q_data.get('title', '').strip()
                content = q_data.get('content', '').strip()
                
                if not title:
                    self.stdout.write(f"Skipping question {post_id}: No title")
                    skipped_q += 1
                    continue
                
                # Create slug
                slug = slugify(title[:100], allow_unicode=True)
                
                # Ensure unique slug
                original_slug = slug
                counter = 1
                while Question.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                # Parse date
                date_str = q_data.get('date') or q_data.get('created')
                try:
                    created_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else datetime.now()
                except:
                    created_at = datetime.now()
                
                # Create question
                question, created = Question.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'title': title,
                        'content': content,
                        'asker_name': 'کاربر',
                        'asker_email': 'user@dadgan.com',
                        'category': category,
                        'views': int(q_data.get('views', 0)),
                        'is_published': True,
                        'is_answered': False,  # Will update after adding answers
                        'created_at': created_at,
                        'seo_title': title[:60],
                        'seo_description': content[:160] if content else '',
                        'seo_keywords': 'مشاوره حقوقی, سوال حقوقی'
                    }
                )
                
                question_map[post_id] = question
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Imported Q: {title[:60]}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⟳ Updated Q: {title[:60]}"))
                imported_q += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error importing question {q_data.get('post_id')}: {e}"))
                skipped_q += 1
        
        # Now import answers
        imported_a = 0
        skipped_a = 0
        
        self.stdout.write("\nImporting Answers...")
        for a_data in answers_data:
            try:
                parent_id = a_data.get('parrent') or a_data.get('parent')
                content = a_data.get('content', '').strip()
                
                if not content:
                    skipped_a += 1
                    continue
                
                # Find parent question
                if parent_id not in question_map:
                    skipped_a += 1
                    continue
                
                question = question_map[parent_id]
                
                # Create answer
                answer, created = Answer.objects.get_or_create(
                    question=question,
                    content=content,
                    defaults={
                        'answerer_name': 'موسسه حقوقی دادگان',
                        'answerer_title': 'مشاور حقوقی',
                        'is_published': True,
                        'is_best_answer': False,
                        'votes': 0
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✓ Added answer to: {question.title[:50]}"))
                    imported_a += 1
                    
                    # Update question to mark as answered
                    question.is_answered = True
                    question.save(update_fields=['is_answered'])
                    
                    # Mark first answer as best answer if it's the only one
                    if question.answers.count() == 1:
                        answer.is_best_answer = True
                        answer.save(update_fields=['is_best_answer'])
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error importing answer: {e}"))
                skipped_a += 1
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"✓ Import Complete!"))
        self.stdout.write(f"  Questions imported/updated: {imported_q}")
        self.stdout.write(f"  Questions skipped: {skipped_q}")
        self.stdout.write(f"  Answers imported: {imported_a}")
        self.stdout.write(f"  Answers skipped: {skipped_a}")
        self.stdout.write(f"  Total questions in database: {Question.objects.count()}")
        self.stdout.write(f"  Total answered questions: {Question.objects.filter(is_answered=True).count()}")
        self.stdout.write(f"{'='*60}")
