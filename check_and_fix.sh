#!/usr/bin/env bash

set -e

# Configuration
VENV_DIR=".venv"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
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

# Check if venv exists
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "Virtual environment not found at $VENV_DIR"
        print_info "Run './manage_site.sh setup' first"
        exit 1
    fi
    source "$VENV_DIR/bin/activate"
}

# Check system issues
check_system() {
    print_info "Checking system requirements..."
    
    local has_errors=0
    
    # Check for required commands
    if ! command -v python &> /dev/null; then
        print_error "Python not found"
        has_errors=1
    else
        print_success "Python $(python --version 2>&1 | awk '{print $2}')"
    fi
    
    if ! command -v pip &> /dev/null; then
        print_error "pip not found"
        has_errors=1
    else
        print_success "pip found"
    fi
    
    return $has_errors
}

# Check Django configuration
check_django() {
    print_info "Checking Django configuration..."
    
    if ! python -c "import django" 2>/dev/null; then
        print_error "Django is not installed"
        return 1
    else
        DJANGO_VERSION=$(python -c "import django; print(django.VERSION[:2])" 2>/dev/null)
        print_success "Django installed (version $DJANGO_VERSION)"
    fi
}

# Check for missing packages
check_packages() {
    print_info "Checking for missing Python packages..."
    
    local missing_packages=()
    
    # Check Pillow
    if ! python -c "import PIL" 2>/dev/null; then
        print_warning "Pillow is not installed (required for ImageField)"
        missing_packages+=("Pillow")
    else
        print_success "Pillow is installed"
    fi
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        return 1
    fi
    return 0
}

# Check for missing directories
check_directories() {
    print_info "Checking for required directories..."
    
    local missing_dirs=()
    
    if [ ! -d "static" ]; then
        print_warning "Missing 'static' directory"
        missing_dirs+=("static")
    else
        print_success "static directory exists"
    fi
    
    if [ ! -d "media" ]; then
        print_warning "Missing 'media' directory"
        missing_dirs+=("media")
    else
        print_success "media directory exists"
    fi
    
    if [ ${#missing_dirs[@]} -gt 0 ]; then
        return 1
    fi
    return 0
}

# Check Django system
check_django_system() {
    print_info "Running Django system check..."
    
    if python manage.py check 2>&1 | tee /tmp/django_check.log; then
        print_success "Django system check passed"
        return 0
    else
        print_error "Django system check failed"
        return 1
    fi
}

# Fix missing packages
fix_packages() {
    print_info "Installing missing packages..."
    
    if command -v uv &> /dev/null; then
        uv pip install Pillow
    else
        pip install Pillow
    fi
    print_success "Installed Pillow"
}

# Fix missing directories
fix_directories() {
    print_info "Creating missing directories..."
    
    mkdir -p static
    print_success "Created static directory"
    
    mkdir -p media
    print_success "Created media directory"
    
    # Create .gitkeep files to ensure directories are tracked
    touch static/.gitkeep
    touch media/.gitkeep
}

# Run all checks
run_checks() {
    print_info "Starting comprehensive diagnostics..."
    echo ""
    
    local has_errors=0
    
    if ! check_system; then
        has_errors=1
    fi
    echo ""
    
    if ! check_django; then
        has_errors=1
    fi
    echo ""
    
    if ! check_packages; then
        has_errors=1
    fi
    echo ""
    
    if ! check_directories; then
        has_errors=1
    fi
    echo ""
    
    if ! check_django_system; then
        has_errors=1
    fi
    echo ""
    
    if [ $has_errors -eq 0 ]; then
        print_success "All checks passed!"
        return 0
    else
        print_warning "Some issues detected"
        return 1
    fi
}

# Run all fixes
run_fixes() {
    print_info "Attempting to fix issues..."
    echo ""
    
    fix_packages
    echo ""
    
    fix_directories
    echo ""
    
    print_info "Running Django system check after fixes..."
    if check_django_system; then
        print_success "All issues fixed!"
        return 0
    else
        print_error "Some issues could not be automatically fixed"
        print_info "See /tmp/django_check.log for details"
        return 1
    fi
}

# Show help
show_help() {
    cat << EOF
${BLUE}Django Project Diagnostic & Fix Tool${NC}

Usage: ./check_and_fix.sh [COMMAND]

Commands:
    check       Run diagnostic checks
    fix         Fix detected issues
    full        Run checks and fix issues
    help        Show this help message

Examples:
    ./check_and_fix.sh check    # Check for issues
    ./check_and_fix.sh fix      # Fix issues
    ./check_and_fix.sh full     # Check and fix

${YELLOW}Checks performed:${NC}
    - Python and pip availability
    - Django installation
    - Required Python packages (Pillow, etc.)
    - Required directories (static, media)
    - Django system integrity

EOF
}

# Main logic
main() {
    COMMAND="${1:-check}"
    
    case "$COMMAND" in
        check)
            check_venv
            run_checks
            ;;
        fix)
            check_venv
            run_fixes
            ;;
        full)
            check_venv
            if run_checks; then
                print_success "No issues to fix"
            else
                echo ""
                read -p "$(echo -e ${YELLOW})Attempt to fix issues? (y/n)${NC} " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    run_fixes
                fi
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
