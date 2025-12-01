#!/usr/bin/env python3
"""
Simple direct SQL parser that works with the exact format from mysqldump
"""

import re
import json

def extract_wordpress_posts():
    print("=" * 60)
    print("Extracting WordPress Posts")
    print("=" * 60)
    
    # WordPress post column names (23 columns as shown in CREATE TABLE)
    columns = [
        'ID', 'post_author', 'post_date', 'post_date_gmt', 'post_content',
        'post_title', 'post_excerpt', 'post_status', 'comment_status', 'ping_status',
        'post_password', 'post_name', 'to_ping', 'pinged', 'post_modified',
        'post_modified_gmt', 'post_content_filtered', 'post_parent', 'guid',
        'menu_order', 'post_type', 'post_mime_type', 'comment_count'
    ]
    
    with open('laravel_backup/c1dadgan.sql', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all wp_posts INSERT statements
    # Match INSERT INTO `wp_posts` VALUES followed by data until semicolon
    insert_pattern = r"INSERT INTO `wp_posts` VALUES\s+(.*?);"
    
    all_posts = []
    matches = re.finditer(insert_pattern, content, re.DOTALL)
    
    for match in matches:
        values_text = match.group(1)
        
        # Parse value tuples: (val1, val2, ...), (val1, val2, ...), ...
        # We need to handle strings with commas and parentheses inside
        records = parse_value_tuples(values_text)
        
        for values in records:
            if len(values) == 23:
                post = dict(zip(columns, values))
                # Only keep published posts of type 'post'
                if post.get('post_status') == 'publish' and post.get('post_type') == 'post':
                    all_posts.append(post)
    
    print(f"Found {len(all_posts)} published blog posts")
    
    # Save to JSON
    with open('data_extraction/wordpress_posts.json', 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2, default=str)
    
    if all_posts:
        print("\nSample posts:")
        for post in all_posts[:3]:
            print(f"  - ID {post['ID']}: {post['post_title'][:60]}")
    
    return all_posts

def extract_qa_posts():
    print("\n" + "=" * 60)
    print("Extracting Q&A Posts")
    print("=" * 60)
    
    # Q&A columns (9 columns based on the data we saw)
    columns = ['post_id', 'postid', 'parrent', 'type', 'title', 'content', 'views', 'date', 'created']
    
    with open('laravel_backup/c1faq.sql', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find all qa_posts INSERT statements
    insert_pattern = r"INSERT INTO `qa_posts` VALUES\s+(.*?);"
    
    all_qa = []
    matches = re.finditer(insert_pattern, content, re.DOTALL)
    
    for match in matches:
        values_text = match.group(1)
        records = parse_value_tuples(values_text)
        
        for values in records:
            if len(values) == 9:
                qa_post = dict(zip(columns, values))
                all_qa.append(qa_post)
    
    print(f"Found {len(all_qa)} Q&A posts")
    
    # Save to JSON
    with open('data_extraction/qa_posts.json', 'w', encoding='utf-8') as f:
        json.dump(all_qa, f, ensure_ascii=False, indent=2, default=str)
    
    # Show stats
    questions = [q for q in all_qa if q.get('type') == 'Q']
    answers = [q for q in all_qa if q.get('type') == 'A']
    print(f"  - Questions: {len(questions)}")
    print(f"  - Answers: {len(answers)}")
    
    if questions:
        print("\nSample questions:")
        for q in questions[:3]:
            print(f"  - ID {q['post_id']}: {q['title'][:60]}")
    
    return all_qa

def parse_value_tuples(text):
    """Parse MySQL value tuples like (val1,val2,...),(val1,val2,...)"""
    results = []
    i = 0
    while i < len(text):
        # Find start of tuple
        while i < len(text) and text[i] not in '(':
            i += 1
        
        if i >= len(text):
            break
        
        # Found opening parenthesis
        i += 1  # Skip '('
        values = []
        current_value = ''
        in_string = False
        string_char = None
        depth = 0
        
        while i < len(text):
            char = text[i]
            
            # Handle escape sequences
            if char == '\\' and i + 1 < len(text) and in_string:
                next_char = text[i + 1]
                if next_char == 'n':
                    current_value += '\n'
                elif next_char == 'r':
                    current_value += '\r'
                elif next_char == 't':
                    current_value += '\t'
                elif next_char in ("'", '"', '\\'):
                    current_value += next_char
                else:
                    current_value += char + next_char
                i += 2
                continue
            
            # Handle string delimiters
            if char in ("'", '"'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and (i == 0 or text[i-1] != '\\'):
                    in_string = False
                    string_char = None
                i += 1
                continue
            
            # Not in string - check for special characters
            if not in_string:
                if char == ',':
                    values.append(parse_value(current_value.strip()))
                    current_value = ''
                    i += 1
                    continue
                elif char == ')':
                    # End of this tuple
                    values.append(parse_value(current_value.strip()))
                    results.append(values)
                    i += 1
                    break
            
            current_value += char
            i += 1
    
    return results

def parse_value(value):
    """Parse a single MySQL value"""
    if not value or value.upper() == 'NULL':
        return None
    
    # Try to parse as number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Return as string
    return value

if __name__ == '__main__':
    wp_posts = extract_wordpress_posts()
    qa_posts = extract_qa_posts()
    
    print("\n" + "=" * 60)
    print("✓ Extraction Complete!")
    print("=" * 60)
    print(f"WordPress blog posts: {len(wp_posts)}")
    print(f"Q&A posts: {len(qa_posts)}")
