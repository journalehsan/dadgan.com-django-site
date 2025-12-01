#!/usr/bin/env python3
"""
Extract WordPress and FAQ data from SQL dumps using regex parsing
"""

import re
import json
from html import unescape

def parse_sql_values(value_str):
    """Parse SQL VALUES string into individual values"""
    values = []
    current = ""
    in_quotes = False
    escape_next = False
    
    for i, char in enumerate(value_str):
        if escape_next:
            current += char
            escape_next = False
        elif char == '\\':
            escape_next = True
            current += char
        elif char == "'" and not escape_next:
            if not in_quotes:
                in_quotes = True
            else:
                # Check if next char is comma or end
                in_quotes = False
        elif char == ',' and not in_quotes:
            values.append(current.strip().strip("'"))
            current = ""
        else:
            current += char
    
    if current:
        values.append(current.strip().strip("'"))
    
    return values

def extract_posts_from_wordpress(sql_file):
    """Extract posts from WordPress SQL dump"""
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    posts = []
    
    # Find the wp_posts CREATE TABLE to get column order
    create_match = re.search(r"CREATE TABLE `wp_posts` \((.*?)\) ENGINE", content, re.DOTALL)
    if not create_match:
        return posts
    
    # Extract column names from CREATE TABLE
    create_def = create_match.group(1)
    columns = []
    for line in create_def.split('\n'):
        if '`' in line:
            col = re.search(r"`(\w+)`", line)
            if col:
                col_name = col.group(1)
                if col_name not in columns:
                    columns.append(col_name)
    
    if not columns:
        return posts
    
    print(f"  wp_posts columns: {', '.join(columns)}")
    
    # Find all INSERT INTO wp_posts statements
    insert_pattern = r"INSERT INTO `wp_posts` VALUES\n(.*?);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    for match in matches:
        # Each row is like (1, 0, '2020-01-01 00:00:00', ...)
        row_pattern = r"\((.*?)\)(?:,|$)"
        rows = re.findall(row_pattern, match)
        
        for row in rows:
            values = parse_sql_values(row)
            
            if len(values) >= len(columns):
                post = {}
                for i, col in enumerate(columns):
                    if i < len(values):
                        val = values[i]
                        # Unescape HTML entities
                        if val and isinstance(val, str):
                            val = unescape(val)
                        post[col] = val
                
                # Only include published posts
                if post.get('post_status') == 'publish':
                    posts.append(post)
    
    return posts

def extract_qa_posts(sql_file):
    """Extract Q&A posts from FAQ SQL dump"""
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    qa_posts = []
    
    # Find the qa_posts CREATE TABLE to get column order
    create_match = re.search(r"CREATE TABLE `qa_posts` \((.*?)\) ENGINE", content, re.DOTALL)
    if not create_match:
        return qa_posts
    
    # Extract column names from CREATE TABLE
    create_def = create_match.group(1)
    columns = []
    for line in create_def.split('\n'):
        if '`' in line:
            col = re.search(r"`(\w+)`", line)
            if col:
                col_name = col.group(1)
                if col_name not in columns:
                    columns.append(col_name)
    
    if not columns:
        return qa_posts
    
    print(f"  qa_posts columns: {', '.join(columns)}")
    
    # Find all INSERT INTO qa_posts statements
    insert_pattern = r"INSERT INTO `qa_posts` VALUES\n(.*?);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    for match in matches:
        # Each row is like (1, '2020-01-01 00:00:00', ...)
        row_pattern = r"\((.*?)\)(?:,|$)"
        rows = re.findall(row_pattern, match)
        
        for row in rows:
            values = parse_sql_values(row)
            
            if len(values) >= len(columns):
                post = {}
                for i, col in enumerate(columns):
                    if i < len(values):
                        val = values[i]
                        if val and isinstance(val, str):
                            val = unescape(val)
                        post[col] = val
                
                qa_posts.append(post)
    
    return qa_posts

# Main execution
print("\n" + "="*70)
print("Extracting WordPress Posts")
print("="*70)

posts = extract_posts_from_wordpress("laravel_backup/c1dadgan.sql")
print(f"✓ Found {len(posts)} published posts")

if posts:
    print("\nSample posts:")
    for post in posts[:5]:
        title = post.get('post_title', 'No title')[:50]
        post_id = post.get('ID', '?')
        post_type = post.get('post_type', 'unknown')
        print(f"  [{post_id}] {post_type}: {title}")

# Save to JSON
with open('data_extraction/wordpress_posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved to data_extraction/wordpress_posts.json")

print("\n" + "="*70)
print("Extracting Q&A Posts")
print("="*70)

qa_posts = extract_qa_posts("laravel_backup/c1faq.sql")
print(f"✓ Found {len(qa_posts)} Q&A posts")

if qa_posts:
    print("\nSample Q&A:")
    for post in qa_posts[:5]:
        title = post.get('title', post.get('question', 'No title'))[:50]
        qa_id = post.get('id', '?')
        print(f"  [{qa_id}] {title}")

# Save to JSON
with open('data_extraction/qa_posts.json', 'w', encoding='utf-8') as f:
    json.dump(qa_posts, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Saved to data_extraction/qa_posts.json")

print("\n" + "="*70)
print("✓ Data extraction complete!")
print("="*70)
