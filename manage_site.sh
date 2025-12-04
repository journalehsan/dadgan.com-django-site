#!/usr/bin/env bash

set -e

# Configuration
VENV_DIR=".venv"
PID_FILE=".django_server.pid"
PORT=8000
HOST="127.0.0.1"

# Default to debug mode for local runs unless explicitly overridden
export DJANGO_DEBUG="${DJANGO_DEBUG:-True}"

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

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Please install it first:"
        echo "  https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    print_success "uv found"
}

# Setup environment
setup_env() {
    print_info "Setting up Python environment with uv..."
    
    if [ ! -d "$VENV_DIR" ]; then
        uv venv "$VENV_DIR"
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Detect shell and activate appropriately
    if [ -n "$FISH_VERSION" ]; then
        source "$VENV_DIR/bin/activate.fish"
    else
        source "$VENV_DIR/bin/activate"
    fi
    print_success "Virtual environment activated"
    
    # Install dependencies
    print_info "Installing dependencies..."
    uv pip install -e .
    print_success "Dependencies installed"
}

# Start Django server
start_server() {
    print_info "Starting Django server..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            print_warning "Server is already running (PID: $PID)"
            return 1
        else
            rm "$PID_FILE"
        fi
    fi
    
    # Detect shell and activate appropriately
    if [ -n "$FISH_VERSION" ]; then
        source "$VENV_DIR/bin/activate.fish"
    else
        source "$VENV_DIR/bin/activate"
    fi
    
    # Run migrations
    print_info "Running migrations..."
    python manage.py migrate
    
    # Start server in background
    nohup python manage.py runserver "$HOST:$PORT" > /tmp/django_server.log 2>&1 &
    echo $! > "$PID_FILE"
    
    print_success "Django server started on http://$HOST:$PORT"
    print_info "PID: $(cat $PID_FILE)"
    print_info "Logs available at: /tmp/django_server.log"
}

# Stop Django server
stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        print_warning "No PID file found. Server may not be running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        print_info "Stopping Django server (PID: $PID)..."
        kill "$PID"
        rm "$PID_FILE"
        sleep 1
        print_success "Django server stopped"
    else
        print_warning "Process with PID $PID not found. Cleaning up..."
        rm "$PID_FILE"
    fi
}

# Restart Django server
restart_server() {
    print_info "Restarting Django server..."
    stop_server || true
    sleep 1
    start_server
}

# Show status
status_server() {
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Server is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if kill -0 "$PID" 2>/dev/null; then
        print_success "Server is running (PID: $PID)"
        print_info "View logs: tail -f /tmp/django_server.log"
    else
        print_warning "PID file exists but process is not running"
        rm "$PID_FILE"
    fi
}

# Show help
show_help() {
    cat << EOF
${BLUE}Django Site Manager${NC}

Usage: ./manage_site.sh [COMMAND]

Commands:
    setup       Create and setup Python environment with uv
    start       Start Django development server
    stop        Stop Django development server
    restart     Restart Django development server
    status      Show server status
    help        Show this help message

Examples:
    ./manage_site.sh setup     # First time setup
    ./manage_site.sh start     # Start the server
    ./manage_site.sh stop      # Stop the server
    ./manage_site.sh restart   # Restart the server

EOF
}

# Main logic
main() {
    COMMAND="${1:-help}"
    
    case "$COMMAND" in
        setup)
            check_uv
            setup_env
            ;;
        start)
            check_uv
            if [ ! -d "$VENV_DIR" ]; then
                print_warning "Environment not set up. Running setup first..."
                setup_env
            fi
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart)
            check_uv
            restart_server
            ;;
        status)
            status_server
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
