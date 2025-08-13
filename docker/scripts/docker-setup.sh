#!/bin/bash

# Docker Setup Script for AI-Powered Scrapy Dashboard
# This script helps you set up and manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs exports httpcache notebooks
    mkdir -p docker/postgres docker/nginx/ssl docker/prometheus docker/grafana/provisioning/datasources docker/grafana/provisioning/dashboards
    
    print_success "Directories created"
}

# Function to create environment file
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file from docker.env..."
        cp docker.env .env
        print_warning "Please edit .env file with your actual credentials before starting the services"
    else
        print_status ".env file already exists"
    fi
}

# Function to build images
build_images() {
    print_status "Building Docker images..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml build
        print_success "Development images built"
    else
        docker-compose build
        print_success "Production images built"
    fi
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml up -d
        print_success "Development services started"
        print_status "Dashboard available at: http://localhost:8502"
        print_status "pgAdmin available at: http://localhost:5050"
        print_status "Redis Commander available at: http://localhost:8081"
        print_status "Jupyter available at: http://localhost:8888"
    else
        docker-compose up -d
        print_success "Production services started"
        print_status "Dashboard available at: http://localhost:8501"
    fi
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml down
        print_success "Development services stopped"
    else
        docker-compose down
        print_success "Production services stopped"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing logs..."
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml logs -f
    else
        docker-compose logs -f
    fi
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up Docker environment..."
        
        if [ "$1" = "dev" ]; then
            docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        else
            docker-compose down -v --remove-orphans
        fi
        
        docker system prune -f
        print_success "Cleanup completed"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show status
show_status() {
    print_status "Service status:"
    
    if [ "$1" = "dev" ]; then
        docker-compose -f docker-compose.dev.yml ps
    else
        docker-compose ps
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTION]"
    echo ""
    echo "Commands:"
    echo "  setup [dev|prod]    - Set up the Docker environment"
    echo "  start [dev|prod]    - Start the services"
    echo "  stop [dev|prod]     - Stop the services"
    echo "  restart [dev|prod]  - Restart the services"
    echo "  logs [dev|prod]     - Show service logs"
    echo "  status [dev|prod]   - Show service status"
    echo "  cleanup [dev|prod]  - Clean up Docker environment"
    echo "  build [dev|prod]    - Build Docker images"
    echo "  help                - Show this help message"
    echo ""
    echo "Options:"
    echo "  dev                 - Use development configuration"
    echo "  prod                - Use production configuration (default)"
    echo ""
    echo "Examples:"
    echo "  $0 setup dev        - Set up development environment"
    echo "  $0 start prod       - Start production services"
    echo "  $0 logs dev         - Show development service logs"
}

# Main script logic
main() {
    local command="$1"
    local environment="${2:-prod}"
    
    case "$command" in
        "setup")
            check_docker
            check_docker_compose
            create_directories
            create_env_file
            build_images "$environment"
            print_success "Setup completed successfully!"
            print_status "Next steps:"
            print_status "1. Edit .env file with your credentials"
            print_status "2. Run: $0 start $environment"
            ;;
        "start")
            check_docker
            check_docker_compose
            start_services "$environment"
            ;;
        "stop")
            check_docker_compose
            stop_services "$environment"
            ;;
        "restart")
            check_docker_compose
            stop_services "$environment"
            sleep 2
            start_services "$environment"
            ;;
        "logs")
            check_docker_compose
            show_logs "$environment"
            ;;
        "status")
            check_docker_compose
            show_status "$environment"
            ;;
        "cleanup")
            check_docker_compose
            cleanup "$environment"
            ;;
        "build")
            check_docker
            check_docker_compose
            build_images "$environment"
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 