#!/usr/bin/env bash

# Script to analyze and extract data from Laravel/WordPress databases for Django migration

set -e

BACKUP_DIR="./laravel_backup"
EXTRACT_DIR="./data_extraction"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Create extraction directory
mkdir -p "$EXTRACT_DIR"

print_info "Analyzing WordPress database (c1dadgan)..."

# Extract posts (articles)
print_info "Extracting blog posts..."
sqlite3 :memory: <(cat <<'EOF'
.mode csv
.output $EXTRACT_DIR/wordpress_posts.csv
SELECT ID, post_title, post_content, post_excerpt, post_status, post_type, post_date 
FROM wp_posts 
WHERE post_status='publish' AND post_type IN ('post', 'page');
EOF
)

# Use Python to extract from SQL dump
python3 << 'PYEOF'
import re
import csv
from pathlib import Path

def extract_insert_data(sql_file, table_name):
    """Extract data from INSERT statements in SQL dump"""
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find INSERT statements for the table
    pattern = rf"INSERT INTO `{table_name}` VALUES \((.*?)\);"
    matches = re.findall(pattern, content, re.DOTALL)
    
    rows = []
    for match in matches:
        # Simple parsing - this might need refinement for complex data
        values = re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", match)
        rows.append([v.strip() for v in values])
    
    return rows

# Extract WordPress posts
print("Extracting WordPress posts...")
db_file = Path("laravel_backup/c1dadgan.sql")
if db_file.exists():
    # Read and analyze the structure
    with open(db_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Find WordPress posts
    post_pattern = r"INSERT INTO `wp_posts` VALUES \((.*?)\);"
    posts = re.findall(post_pattern, content, re.DOTALL)
    
    print(f"Found {len(posts)} posts in database")
    
    # Extract meta information
    with open("data_extraction/wordpress_analysis.txt", 'w', encoding='utf-8') as f:
        f.write("# WordPress Database Analysis\n\n")
        f.write(f"Total posts found: {len(posts)}\n\n")
        
        # Show sample posts
        if posts:
            f.write("## Sample Posts:\n\n")
            for i, post in enumerate(posts[:5]):
                f.write(f"### Post {i+1}\n")
                f.write(f"Data: {post[:200]}...\n\n")

# Extract FAQ posts
print("Extracting FAQ posts...")
faq_file = Path("laravel_backup/c1faq.sql")
if faq_file.exists():
    with open(faq_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    qa_pattern = r"INSERT INTO `qa_posts` VALUES \((.*?)\);"
    qa_posts = re.findall(qa_pattern, content, re.DOTALL)
    
    print(f"Found {len(qa_posts)} Q&A posts in database")
    
    with open("data_extraction/faq_analysis.txt", 'w', encoding='utf-8') as f:
        f.write("# FAQ/Q&A Database Analysis\n\n")
        f.write(f"Total Q&A posts found: {len(qa_posts)}\n\n")
        
        if qa_posts:
            f.write("## Sample Q&A Posts:\n\n")
            for i, post in enumerate(qa_posts[:5]):
                f.write(f"### Post {i+1}\n")
                f.write(f"Data: {post[:200]}...\n\n")

print("✓ Analysis complete")

PYEOF

print_success "Data extraction complete!"
print_info "Check $EXTRACT_DIR for extracted data"
