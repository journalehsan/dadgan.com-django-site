#!/usr/bin/env bash

# Remote server configuration
REMOTE_HOST="rocky@37.32.13.22"
REMOTE_PORT=22
REMOTE_PASSWORD="Trk@#1403"
DOCKER_CONTAINER="dadgan_app"
LOCAL_BACKUP_DIR="./laravel_backup"

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

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check for required tools
check_requirements() {
    print_info "Checking required tools..."
    
    if ! command -v sshpass &> /dev/null; then
        print_error "sshpass is not installed"
        echo "Install with: sudo apt-get install sshpass (Debian/Ubuntu) or brew install sshpass (macOS)"
        exit 1
    fi
    print_success "sshpass found"
    
    if ! command -v ssh &> /dev/null; then
        print_error "ssh is not installed"
        exit 1
    fi
    print_success "ssh found"
}

# Create backup directory
create_backup_dir() {
    print_info "Creating backup directory..."
    mkdir -p "$LOCAL_BACKUP_DIR"
    print_success "Backup directory created at $LOCAL_BACKUP_DIR"
}

# Test SSH connection
test_connection() {
    print_info "Testing SSH connection to $REMOTE_HOST..."
    
    if sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE_HOST" "echo 'Connection successful'" 2>&1 | grep -q "Connection successful"; then
        print_success "SSH connection successful"
        return 0
    else
        print_error "SSH connection failed"
        return 1
    fi
}

# Export Laravel database
export_database() {
    print_info "Exporting databases from Laravel configuration..."
    
    # Database credentials from Laravel config
    DB_HOST="docker-mariadb-phpmyadmin-mariadb-1"
    DB_USER="root"
    DB_PASS="my-secret-pw"
    DB_NAME1="c1dadgan"
    DB_NAME2="c1faq"
    DB_CONTAINER="docker-mariadb-phpmyadmin-mariadb-1"
    
    # Export main database (c1dadgan) using mariadb-dump
    print_info "Exporting database: $DB_NAME1..."
    sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE_HOST" \
        "docker exec $DB_CONTAINER mariadb-dump -h localhost -u $DB_USER -p$DB_PASS $DB_NAME1 > /tmp/${DB_NAME1}.sql 2>&1" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Database $DB_NAME1 dumped on remote server"
        
        # Download the dump
        sshpass -p "$REMOTE_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
            "$REMOTE_HOST:/tmp/${DB_NAME1}.sql" "$LOCAL_BACKUP_DIR/${DB_NAME1}.sql" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Database $DB_NAME1 downloaded"
            ls -lh "$LOCAL_BACKUP_DIR/${DB_NAME1}.sql"
        else
            print_error "Failed to download database $DB_NAME1"
        fi
    else
        print_error "Failed to export database $DB_NAME1"
    fi
    
    # Export FAQ database (c1faq) using mariadb-dump
    print_info "Exporting database: $DB_NAME2..."
    sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE_HOST" \
        "docker exec $DB_CONTAINER mariadb-dump -h localhost -u $DB_USER -p$DB_PASS $DB_NAME2 > /tmp/${DB_NAME2}.sql 2>&1" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Database $DB_NAME2 dumped on remote server"
        
        # Download the dump
        sshpass -p "$REMOTE_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
            "$REMOTE_HOST:/tmp/${DB_NAME2}.sql" "$LOCAL_BACKUP_DIR/${DB_NAME2}.sql" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Database $DB_NAME2 downloaded"
            ls -lh "$LOCAL_BACKUP_DIR/${DB_NAME2}.sql"
        else
            print_error "Failed to download database $DB_NAME2"
        fi
    else
        print_error "Failed to export database $DB_NAME2"
    fi
}

# Extract Laravel application files
extract_laravel_files() {
    print_info "Extracting Laravel application files..."
    
    sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$REMOTE_HOST" \
        "docker exec $DOCKER_CONTAINER tar czf /tmp/dadgan_app.tar.gz /var/www/html" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Laravel app archived on remote server"
        
        print_info "Downloading Laravel app..."
        sshpass -p "$REMOTE_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
            "$REMOTE_HOST:/tmp/dadgan_app.tar.gz" "$LOCAL_BACKUP_DIR/dadgan_app.tar.gz" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Laravel app downloaded"
            print_info "Extracting files..."
            cd "$LOCAL_BACKUP_DIR"
            tar xzf dadgan_app.tar.gz
            cd - > /dev/null
            print_success "Laravel files extracted"
        else
            print_error "Failed to download Laravel app"
            return 1
        fi
    else
        print_error "Failed to archive Laravel app"
        return 1
    fi
}

# Extract blade template contents
extract_blade_templates() {
    print_info "Extracting Blade template contents..."
    
    if [ -d "$LOCAL_BACKUP_DIR/var/www/html/resources/views" ]; then
        print_success "Found Blade templates directory"
        
        # Create a summary file
        {
            echo "# Blade Templates Content Summary"
            echo "## Extracted on $(date)"
            echo ""
            
            find "$LOCAL_BACKUP_DIR/var/www/html/resources/views" -name "*.blade.php" -type f | while read file; do
                relative_path="${file#$LOCAL_BACKUP_DIR/var/www/html/}"
                echo "## File: $relative_path"
                echo '```php'
                head -50 "$file"
                echo '```'
                echo ""
            done
        } > "$LOCAL_BACKUP_DIR/blade_templates_summary.md"
        
        print_success "Blade templates summary created"
    else
        print_warning "Blade templates directory not found"
    fi
}

# Extract database schema info
extract_schema_info() {
    print_info "Extracting database schema information..."
    
    if [ -f "$LOCAL_BACKUP_DIR/dadgan_laravel.sql" ]; then
        {
            echo "# Database Schema Information"
            echo "## Extracted on $(date)"
            echo ""
            echo "## Tables"
            echo '```sql'
            grep "CREATE TABLE" "$LOCAL_BACKUP_DIR/dadgan_laravel.sql"
            echo '```'
            echo ""
        } > "$LOCAL_BACKUP_DIR/database_schema.md"
        
        print_success "Database schema info extracted"
    fi
}

# Create migration guide
create_migration_guide() {
    print_info "Creating migration guide..."
    
    {
        echo "# Laravel to Django Migration Guide"
        echo "## Date: $(date)"
        echo ""
        echo "### Files Available for Migration:"
        echo ""
        echo "1. **dadgan_laravel.sql** - Complete MySQL database dump"
        echo "2. **dadgan_app.tar.gz** - Complete Laravel application"
        echo "3. **blade_templates_summary.md** - Summary of Blade templates"
        echo "4. **database_schema.md** - Database schema information"
        echo ""
        echo "### Next Steps:"
        echo ""
        echo "1. Analyze the database schema"
        echo "2. Create corresponding Django models"
        echo "3. Write migration script to import data"
        echo "4. Extract content from Blade templates"
        echo "5. Create Django templates with SEO optimization"
        echo ""
        echo "### SEO Optimization Focus:"
        echo "- Keyword: موسسه حقوقی (Legal Institution/Law Firm)"
        echo "- Add meta tags for Farsi/Persian content"
        echo "- Optimize URL structure"
        echo "- Add structured data (Schema.org)"
        echo ""
    } > "$LOCAL_BACKUP_DIR/MIGRATION_GUIDE.md"
    
    print_success "Migration guide created"
}

# Show help
show_help() {
    cat << EOF
${BLUE}Laravel to Django Migration Tool${NC}

Usage: ./migrate_from_laravel.sh [COMMAND]

Commands:
    test        Test SSH connection only
    export-db   Export database only
    export-app  Export Laravel application only
    full        Run complete migration (recommended)
    help        Show this help message

Examples:
    ./migrate_from_laravel.sh test      # Test connection
    ./migrate_from_laravel.sh full      # Full migration
    
${YELLOW}Configuration:${NC}
    Remote Host: $REMOTE_HOST
    Docker Container: $DOCKER_CONTAINER
    Backup Directory: $LOCAL_BACKUP_DIR

EOF
}

# Main logic
main() {
    COMMAND="${1:-help}"
    
    case "$COMMAND" in
        test)
            check_requirements
            test_connection
            ;;
        export-db)
            check_requirements
            create_backup_dir
            export_database
            extract_schema_info
            ;;
        export-app)
            check_requirements
            create_backup_dir
            extract_laravel_files
            extract_blade_templates
            ;;
        full)
            check_requirements
            create_backup_dir
            test_connection
            if [ $? -eq 0 ]; then
                export_database
                extract_schema_info
                extract_laravel_files
                extract_blade_templates
                create_migration_guide
                print_success "Migration data collection complete!"
                print_info "Check $LOCAL_BACKUP_DIR for all extracted files"
            else
                print_error "Connection test failed, aborting migration"
                exit 1
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
