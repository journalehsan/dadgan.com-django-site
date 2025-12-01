#!/usr/bin/env python3
"""
Script to analyze and extract data from Laravel/WordPress databases for Django migration
"""

import re
import json
from pathlib import Path
from collections import defaultdict
import html

class SQLDumpAnalyzer:
    def __init__(self, sql_file):
        self.sql_file = sql_file
        self.content = None
        self.tables = defaultdict(list)
        
    def load(self):
        """Load SQL dump file"""
        with open(self.sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            self.content = f.read()
        print(f"✓ Loaded {self.sql_file}")
        
    def extract_table_schema(self, table_name):
        """Extract CREATE TABLE statement"""
        pattern = rf"CREATE TABLE `{table_name}` \((.*?)\) ENGINE"
        match = re.search(pattern, self.content, re.DOTALL)
        if match:
            return match.group(1)
        return None
    
    def extract_insert_rows(self, table_name, limit=None):
        """Extract INSERT rows for a table"""
        # Find all INSERT statements for this table
        pattern = rf"INSERT INTO `{table_name}` \((.*?)\) VALUES (.*?);"
        match = re.search(pattern, self.content, re.DOTALL)
        
        if not match:
            return []
        
        columns_str = match.group(1)
        values_str = match.group(2)
        
        # Parse columns
        columns = [col.strip().strip('`') for col in columns_str.split(',')]
        
        # Parse values - this is simplified, real parsing would be more complex
        rows = []
        value_pattern = r"\((.*?)\)"
        value_matches = re.findall(value_pattern, values_str, re.DOTALL)
        
        for i, value_group in enumerate(value_matches):
            if limit and len(rows) >= limit:
                break
                
            # Split values, handling quoted strings
            values = []
            current = ""
            in_quotes = False
            
            for char in value_group:
                if char == "'" and (not current or current[-1] != "\\"):
                    in_quotes = not in_quotes
                    current += char
                elif char == "," and not in_quotes:
                    values.append(current.strip())
                    current = ""
                else:
                    current += char
            
            if current:
                values.append(current.strip())
            
            # Clean values
            cleaned = []
            for val in values:
                if val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                    val = val.replace("\\'", "'")
                    val = val.replace('\\"', '"')
                cleaned.append(val)
            
            if len(cleaned) == len(columns):
                row = dict(zip(columns, cleaned))
                rows.append(row)
        
        return rows
    
    def get_summary(self):
        """Get summary of tables in the dump"""
        # Find all CREATE TABLE statements
        pattern = r"CREATE TABLE `(\w+)`"
        tables = re.findall(pattern, self.content)
        return list(set(tables))

# Analyze WordPress database
print("\n" + "="*60)
print("Analyzing WordPress Database (c1dadgan)")
print("="*60)

wp_analyzer = SQLDumpAnalyzer("laravel_backup/c1dadgan.sql")
wp_analyzer.load()

wp_tables = wp_analyzer.get_summary()
print(f"\nTables found: {', '.join(wp_tables)}\n")

# Extract posts
print("Extracting blog posts (wp_posts)...")
posts = wp_analyzer.extract_insert_rows("wp_posts", limit=10)
print(f"Found {len(posts)} posts (showing first 10)")

posts_data = {
    'count': len(wp_analyzer.extract_insert_rows("wp_posts")),
    'sample_posts': posts
}

with open('data_extraction/wordpress_posts.json', 'w', encoding='utf-8') as f:
    json.dump(posts_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved to data_extraction/wordpress_posts.json")

# Analyze FAQ database
print("\n" + "="*60)
print("Analyzing FAQ Database (c1faq)")
print("="*60)

faq_analyzer = SQLDumpAnalyzer("laravel_backup/c1faq.sql")
faq_analyzer.load()

faq_tables = faq_analyzer.get_summary()
print(f"\nTables found: {', '.join(faq_tables)}\n")

# Extract Q&A posts
print("Extracting Q&A posts (qa_posts)...")
qa_posts = faq_analyzer.extract_insert_rows("qa_posts", limit=10)
print(f"Found {len(qa_posts)} Q&A posts (showing first 10)")

qa_data = {
    'count': len(faq_analyzer.extract_insert_rows("qa_posts")),
    'sample_posts': qa_posts
}

with open('data_extraction/qa_posts.json', 'w', encoding='utf-8') as f:
    json.dump(qa_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved to data_extraction/qa_posts.json")

print("\n" + "="*60)
print("✓ Data extraction complete!")
print("="*60)
