#!/usr/bin/env python3
"""
Improved script to extract data from MySQL dumps without using database import
Parses MySQL INSERT statements directly
"""

import re
import json
import html
from pathlib import Path

def parse_mysql_value(value):
    """Parse a MySQL value (string, number, NULL)"""
    value = value.strip()
    
    if value.upper() == 'NULL':
        return None
    
    # If it's a string (starts and ends with quotes)
    if (value.startswith("'") and value.endswith("'")) or \
       (value.startswith('"') and value.endswith('"')):
        # Remove quotes and unescape
        value = value[1:-1]
        # Unescape MySQL escapes
        value = value.replace("\\'", "'")
        value = value.replace('\\"', '"')
        value = value.replace('\\n', '\n')
        value = value.replace('\\r', '\r')
        value = value.replace('\\\\', '\\')
        return value
    
    # Try to convert to number
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value

def parse_insert_values(sql_content, table_name):
    """Extract INSERT VALUES from SQL dump"""
    # Find all INSERT INTO statements for the table - match across multiple lines
    pattern = rf'INSERT INTO `{table_name}` VALUES\s+(.*?)(?:;|\nINSERT|\n\/\*|\nUNLOCK|\n--)'
    matches = re.finditer(pattern, sql_content, re.DOTALL | re.MULTILINE)
    
    all_records = []
    
    for match in matches:
        values_block = match.group(1).strip()
        
        # Use a more robust parser for VALUES
        # Find all complete value tuples
        depth = 0
        in_string = False
        escape_next = False
        string_char = None
        current_record = ''
        records_text = []
        
        for i, char in enumerate(values_block):
            if escape_next:
                current_record += char
                escape_next = False
                continue
            
            if char == '\\' and in_string:
                current_record += char
                escape_next = True
                continue
            
            if char in ("'", '"') and not escape_next:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                current_record += char
                continue
            
            if not in_string:
                if char == '(':
                    depth += 1
                    if depth == 1:
                        current_record = ''
                        continue
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        records_text.append(current_record.strip())
                        current_record = ''
                        continue
            
            if depth > 0:
                current_record += char
        
        # Parse each record
        for record_text in records_text:
            fields = []
            current_field = ''
            in_quotes = False
            quote_char = None
            escape_next = False
            
            for char in record_text:
                if escape_next:
                    current_field += char
                    escape_next = False
                    continue
                
                if char == '\\':
                    current_field += char
                    escape_next = True
                    continue
                
                if char in ("'", '"') and not escape_next:
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                    current_field += char
                elif char == ',' and not in_quotes:
                    fields.append(parse_mysql_value(current_field))
                    current_field = ''
                else:
                    current_field += char
            
            # Don't forget the last field
            if current_field:
                fields.append(parse_mysql_value(current_field))
            
            if fields:  # Only add non-empty records
                all_records.append(fields)
    
    return all_records

def extract_wordpress_posts(sql_file, output_file):
    """Extract WordPress posts from SQL dump"""
    print(f"\n{'='*60}")
    print("Extracting WordPress Posts")
    print(f"{'='*60}")
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        sql_content = f.read()
    
    # Get column names from CREATE TABLE
    create_pattern = r'CREATE TABLE `wp_posts` \((.*?)\) ENGINE'
    create_match = re.search(create_pattern, sql_content, re.DOTALL)
    
    if create_match:
        columns_def = create_match.group(1)
        # Extract column names
        col_pattern = r'`(\w+)`\s+'
        columns = re.findall(col_pattern, columns_def)
        print(f"Columns found: {len(columns)}")
        print(f"Column names: {', '.join(columns[:10])}...")
    else:
        print("Could not find table structure!")
        return []
    
    # Extract data
    records = parse_insert_values(sql_content, 'wp_posts')
    print(f"Total records extracted: {len(records)}")
    
    # Convert to dictionaries
    all_posts = []
    for record in records:
        if len(record) >= len(columns):
            post_dict = dict(zip(columns, record[:len(columns)]))
            all_posts.append(post_dict)
        elif len(record) > 0:
            print(f"Warning: Record has {len(record)} fields, expected {len(columns)}")
    
    # Filter for published posts of type 'post'
    posts = [p for p in all_posts if p.get('post_status') == 'publish' and p.get('post_type') == 'post']
    
    print(f"Total records extracted with correct field count: {len(all_posts)}")
    print(f"Published 'post' type posts: {len(posts)}")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✓ Saved to {output_file}")
    
    # Show samples
    if posts:
        print("\nSample posts:")
        for post in posts[:3]:
            print(f"  - ID {post.get('ID')}: {post.get('post_title', '')[:60]}")
    
    return posts

def extract_qa_posts(sql_file, output_file):
    """Extract Q&A posts from SQL dump"""
    print(f"\n{'='*60}")
    print("Extracting Q&A Posts")
    print(f"{'='*60}")
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        sql_content = f.read()
    
    # Get column names from CREATE TABLE
    create_pattern = r'CREATE TABLE `qa_posts` \((.*?)\) ENGINE'
    create_match = re.search(create_pattern, sql_content, re.DOTALL)
    
    if create_match:
        columns_def = create_match.group(1)
        col_pattern = r'`(\w+)`\s+'
        columns = re.findall(col_pattern, columns_def)
        print(f"Columns found: {len(columns)}")
        print(f"Column names: {', '.join(columns)}")
    else:
        print("Could not find table structure!")
        return []
    
    # Extract data
    records = parse_insert_values(sql_content, 'qa_posts')
    print(f"Total records extracted: {len(records)}")
    
    # Convert to dictionaries
    qa_posts = []
    for record in records:
        if len(record) >= len(columns):
            qa_dict = dict(zip(columns, record[:len(columns)]))
            qa_posts.append(qa_dict)
        elif len(record) > 0:
            print(f"Warning: Record has {len(record)} fields, expected {len(columns)}")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_posts, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"✓ Saved to {output_file}")
    
    # Show samples
    if qa_posts:
        print("\nSample Q&A posts:")
        for post in qa_posts[:5]:
            post_type = post.get('type', 'Q')
            title = post.get('title', '')
            print(f"  - [{post_type}] {post.get('post_id')}: {title[:60]}")
    
    return qa_posts

def main():
    # Create data extraction directory if it doesn't exist
    Path('data_extraction').mkdir(exist_ok=True)
    
    # Extract WordPress posts
    wp_posts = extract_wordpress_posts(
        'laravel_backup/c1dadgan.sql',
        'data_extraction/wordpress_posts.json'
    )
    
    # Extract Q&A posts
    qa_posts = extract_qa_posts(
        'laravel_backup/c1faq.sql',
        'data_extraction/qa_posts.json'
    )
    
    print(f"\n{'='*60}")
    print("✓ Extraction Complete!")
    print(f"{'='*60}")
    print(f"WordPress posts: {len(wp_posts)}")
    print(f"Q&A posts: {len(qa_posts)}")
    print("\nFiles created:")
    print("  - data_extraction/wordpress_posts.json")
    print("  - data_extraction/qa_posts.json")

if __name__ == '__main__':
    main()
