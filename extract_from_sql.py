#!/usr/bin/env python3
"""
Extract data from SQL dumps using SQLite
"""

import sqlite3
import json
import re
import os
from pathlib import Path

def import_sql_to_sqlite(sql_file, db_connection):
    """Import SQL dump into SQLite database"""
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        sql = f.read()
    
    # SQLite doesn't support all MySQL syntax, so we need to clean it
    # Remove MySQL-specific statements
    sql = re.sub(r'\/\*!.*?\*\/', '', sql, flags=re.DOTALL)  # Remove /*! ... */
    sql = re.sub(r'^\s*--.*?$', '', sql, flags=re.MULTILINE)  # Remove comments
    
    # Split by semicolon and execute
    statements = sql.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                db_connection.execute(statement)
            except Exception as e:
                # Skip problematic statements
                pass
    
    db_connection.commit()

def extract_posts(db_file, sql_file, table_name, output_file):
    """Extract posts from SQL file using SQLite"""
    
    # Create in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    print(f"Loading {sql_file}...")
    import_sql_to_sqlite(sql_file, conn)
    
    cursor = conn.cursor()
    
    # Get table info
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Table '{table_name}' columns: {', '.join(columns)}")
    except Exception as e:
        print(f"Error getting table info: {e}")
        return
    
    # Extract data
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(row))
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Extracted {len(data)} records to {output_file}")
        return data
    
    except Exception as e:
        print(f"Error extracting data: {e}")
        return []

print("="*60)
print("WordPress Database Analysis")
print("="*60)

# Extract WordPress posts
posts = extract_posts(
    ":memory:",
    "laravel_backup/c1dadgan.sql",
    "wp_posts",
    "data_extraction/wordpress_posts.json"
)

if posts:
    print("\nSample posts:")
    for post in posts[:3]:
        print(f"  - {post.get('ID', '?')}: {post.get('post_title', 'No title')[:60]}")

print("\n" + "="*60)
print("FAQ Database Analysis")
print("="*60)

# Extract FAQ posts
qa_posts = extract_posts(
    ":memory:",
    "laravel_backup/c1faq.sql",
    "qa_posts",
    "data_extraction/qa_posts.json"
)

if qa_posts:
    print("\nSample Q&A:")
    for post in qa_posts[:3]:
        title = post.get('title', post.get('question', 'No title'))
        print(f"  - {post.get('id', '?')}: {title[:60]}")

print("\n" + "="*60)
print("✓ Analysis complete!")
print("="*60)
