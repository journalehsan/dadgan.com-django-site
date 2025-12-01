#!/usr/bin/env python3
"""
Import Q&A posts into Django
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the project directory to the path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dadgan_project.settings')
import django
django.setup()

from django.utils.text import slugify
from lawfirm.models import Question, QACategory, Answer

def import_qa_posts():
    print("=" * 60)
    print("Importing Q&A Posts")
    print("=" * 60)
    
    # Load JSON data
    with open('data_extraction/qa_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"Found {len(posts)} Q&A posts to import")
    
    # Get or create default category
    category, _ = QACategory.objects.get_or_create(
        slug='general',
        defaults={
            'name': 'سوالات عمومی',
            'description': 'سوالات و پاسخ‌های عمومی حقوقی'
        }
    )
    
    # Separate questions and answers
    questions_data = [p for p in posts if p.get('type') == 'Q']
    answers_data = [p for p in posts if p.get('type') == 'A']
    
    print(f"  Questions: {len(questions_data)}")
    print(f"  Answers: {len(answers_data)}")
    
    # First import all questions
    question_map = {}  # Map old post_id to new Question object
    imported_q = 0
    skipped_q = 0
    
    print("\nImporting Questions...")
    for q_data in questions_data:
        try:
            post_id = q_data.get('post_id')
            title = q_data.get('title', '').strip()
            content = q_data.get('content', '').strip()
            
            if not title:
                print(f"Skipping question {post_id}: No title")
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
                print(f"✓ Imported Q: {title[:60]}")
            else:
                print(f"⟳ Updated Q: {title[:60]}")
            imported_q += 1
            
        except Exception as e:
            print(f"✗ Error importing question {q_data.get('post_id')}: {e}")
            skipped_q += 1
    
    # Now import answers
    imported_a = 0
    skipped_a = 0
    
    print("\nImporting Answers...")
    for a_data in answers_data:
        try:
            parent_id = a_data.get('parrent') or a_data.get('parent')
            content = a_data.get('content', '').strip()
            
            if not content:
                print(f"Skipping answer: No content")
                skipped_a += 1
                continue
            
            # Find parent question
            if parent_id not in question_map:
                print(f"Skipping answer: Parent question {parent_id} not found")
                skipped_a += 1
                continue
            
            question = question_map[parent_id]
            
            # Parse date
            date_str = a_data.get('date') or a_data.get('created')
            try:
                created_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') if date_str else datetime.now()
            except:
                created_at = datetime.now()
            
            # Create answer
            answer, created = Answer.objects.get_or_create(
                question=question,
                content=content,
                defaults={
                    'answerer_name': 'موسسه حقوقی دادگان',
                    'answerer_title': 'مشاور حقوقی',
                    'is_published': True,
                    'is_best_answer': False,  # First answer will be marked as best
                    'votes': 0
                }
            )
            
            if created:
                print(f"✓ Added answer to: {question.title[:50]}")
                imported_a += 1
                
                # Update question to mark as answered
                question.is_answered = True
                question.save(update_fields=['is_answered'])
                
                # Mark first answer as best answer if it's the only one
                if question.answers.count() == 1:
                    answer.is_best_answer = True
                    answer.save(update_fields=['is_best_answer'])
            
        except Exception as e:
            print(f"✗ Error importing answer: {e}")
            skipped_a += 1
    
    print(f"\n{'='*60}")
    print(f"✓ Import Complete!")
    print(f"  Questions imported/updated: {imported_q}")
    print(f"  Questions skipped: {skipped_q}")
    print(f"  Answers imported: {imported_a}")
    print(f"  Answers skipped: {skipped_a}")
    print(f"  Total questions in database: {Question.objects.count()}")
    print(f"  Total answered questions: {Question.objects.filter(is_answered=True).count()}")
    print(f"{'='*60}")

if __name__ == '__main__':
    import_qa_posts()
