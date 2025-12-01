#!/usr/bin/env python3
"""
Import WordPress blog posts into Django
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

from django.contrib.auth.models import User
from django.utils.text import slugify
from lawfirm.models import BlogPost, Category

def import_wordpress_posts():
    print("=" * 60)
    print("Importing WordPress Blog Posts")
    print("=" * 60)
    
    # Load JSON data
    with open('data_extraction/wordpress_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"Found {len(posts)} posts to import")
    
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
            'description': 'مقالات عمومی'
        }
    )
    
    imported = 0
    skipped = 0
    
    for post_data in posts:
        try:
            post_id = post_data.get('ID')
            title = post_data.get('post_title', '').strip()
            
            if not title:
                print(f"Skipping post {post_id}: No title")
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
                # Create excerpt from content
                excerpt = content[:297] + '...' if len(content) > 300 else content
            
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
                    'excerpt': excerpt,
                    'content': content,
                    'published': True,
                    'featured': imported < 3,  # First 3 as featured
                    'views': 0,
                    'created_at': created_at,
                    'seo_title': title[:60],
                    'seo_description': excerpt[:160] if excerpt else '',
                    'seo_keywords': 'موسسه حقوقی, مشاوره حقوقی, وکیل'
                }
            )
            
            if created:
                print(f"✓ Imported: {title[:60]}")
                imported += 1
            else:
                print(f"⟳ Updated: {title[:60]}")
                imported += 1
                
        except Exception as e:
            print(f"✗ Error importing post {post_data.get('ID')}: {e}")
            skipped += 1
    
    print(f"\n{'='*60}")
    print(f"✓ Import Complete!")
    print(f"  Imported/Updated: {imported}")
    print(f"  Skipped: {skipped}")
    print(f"  Total in database: {BlogPost.objects.count()}")
    print(f"{'='*60}")

if __name__ == '__main__':
    import_wordpress_posts()
