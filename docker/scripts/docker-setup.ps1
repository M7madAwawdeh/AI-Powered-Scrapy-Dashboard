# Docker Setup Script for AI-Powered Scrapy Dashboard (PowerShell)
# This script helps you set up and manage the Docker environment on Windows

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "prod"
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop and try again."
        return $false
    }
}

# Function to check if Docker Compose is available
function Test-DockerCompose {
    try {
        docker-compose --version | Out-Null
        Write-Success "Docker Compose is available"
        return $true
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose and try again."
        return $false
    }
}

# Function to create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    
    $directories = @(
        "logs",
        "exports", 
        "httpcache",
        "notebooks",
        "docker/postgres",
        "docker/nginx/ssl",
        "docker/prometheus",
        "docker/grafana/provisioning/datasources",
        "docker/grafana/provisioning/dashboards"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directories created"
}

# Function to create environment file
function New-EnvFile {
    if (!(Test-Path ".env")) {
        Write-Status "Creating .env file from docker.env..."
        Copy-Item "docker.env" ".env"
        Write-Warning "Please edit .env file with your actual credentials before starting the services"
    }
    else {
        Write-Status ".env file already exists"
    }
}

# Function to build images
function Build-Images {
    Write-Status "Building Docker images..."
    
    if ($Environment -eq "dev") {
        docker-compose -f docker-compose.dev.yml build
        Write-Success "Development images built"
    }
    else {
        docker-compose build
        Write-Success "Production images built"
    }
}

# Function to start services
function Start-Services {
    Write-Status "Starting services..."
    
    if ($Environment -eq "dev") {
        docker-compose -f docker-compose.dev.yml up -d
        Write-Success "Development services started"
        Write-Status "Dashboard available at: http://localhost:8502"
        Write-Status "pgAdmin available at: http://localhost:5050"
        Write-Status "Redis Commander available at: http://localhost:8081"
        Write-Status "Jupyter available at: http://localhost:8888"
    }
    else {
        docker-compose up -d
        Write-Success "Production services started"
        Write-Status "Dashboard available at: http://localhost:8501"
    }
}

# Function to stop services
function Stop-Services {
    Write-Status "Stopping services..."
    
    if ($Environment -eq "dev") {
        docker-compose -f docker-compose.dev.yml down
        Write-Success "Development services stopped"
    }
    else {
        docker-compose down
        Write-Success "Production services stopped"
    }
}

# Function to show logs
function Show-Logs {
    Write-Status "Showing logs..."
    
    if ($Environment -eq "dev") {
        docker-compose -f docker-compose.dev.yml logs -f
    }
    else {
        docker-compose logs -f
    }
}

# Function to clean up
function Remove-All {
    Write-Warning "This will remove all containers, networks, and volumes. Are you sure? (y/N)"
    $response = Read-Host
    
    if ($response -match "^[yY]$|^[yY][eE][sS]$") {
        Write-Status "Cleaning up Docker environment..."
        
        if ($Environment -eq "dev") {
            docker-compose -f docker-compose.dev.yml down -v --remove-orphans
        }
        else {
            docker-compose down -v --remove-orphans
        }
        
        docker system prune -f
        Write-Success "Cleanup completed"
    }
    else {
        Write-Status "Cleanup cancelled"
    }
}

# Function to show status
function Show-Status {
    Write-Status "Service status:"
    
    if ($Environment -eq "dev") {
        docker-compose -f docker-compose.dev.yml ps
    }
    else {
        docker-compose ps
    }
}

# Function to show help
function Show-Help {
    Write-Host "Usage: .\docker-setup.ps1 [COMMAND] [OPTION]" -ForegroundColor $White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor $White
    Write-Host "  setup [dev|prod]    - Set up the Docker environment" -ForegroundColor $White
    Write-Host "  start [dev|prod]    - Start the services" -ForegroundColor $White
    Write-Host "  stop [dev|prod]     - Stop the services" -ForegroundColor $White
    Write-Host "  restart [dev|prod]  - Restart the services" -ForegroundColor $White
    Write-Host "  logs [dev|prod]     - Show service logs" -ForegroundColor $White
    Write-Host "  status [dev|prod]   - Show service status" -ForegroundColor $White
    Write-Host "  cleanup [dev|prod]  - Clean up Docker environment" -ForegroundColor $White
    Write-Host "  build [dev|prod]    - Build Docker images" -ForegroundColor $White
    Write-Host "  help                - Show this help message" -ForegroundColor $White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor $White
    Write-Host "  dev                 - Use development configuration" -ForegroundColor $White
    Write-Host "  prod                - Use production configuration (default)" -ForegroundColor $White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor $White
    Write-Host "  .\docker-setup.ps1 setup dev        - Set up development environment" -ForegroundColor $White
    Write-Host "  .\docker-setup.ps1 start prod       - Start production services" -ForegroundColor $White
    Write-Host "  .\docker-setup.ps1 logs dev         - Show development service logs" -ForegroundColor $White
}

# Main script logic
function Main {
    switch ($Command.ToLower()) {
        "setup" {
            if (!(Test-Docker)) { exit 1 }
            if (!(Test-DockerCompose)) { exit 1 }
            New-Directories
            New-EnvFile
            Build-Images
            Write-Success "Setup completed successfully!"
            Write-Status "Next steps:"
            Write-Status "1. Edit .env file with your credentials"
            Write-Status "2. Run: .\docker-setup.ps1 start $Environment"
        }
        "start" {
            if (!(Test-Docker)) { exit 1 }
            if (!(Test-DockerCompose)) { exit 1 }
            Start-Services
        }
        "stop" {
            if (!(Test-DockerCompose)) { exit 1 }
            Stop-Services
        }
        "restart" {
            if (!(Test-DockerCompose)) { exit 1 }
            Stop-Services
            Start-Sleep -Seconds 2
            Start-Services
        }
        "logs" {
            if (!(Test-DockerCompose)) { exit 1 }
            Show-Logs
        }
        "status" {
            if (!(Test-DockerCompose)) { exit 1 }
            Show-Status
        }
        "cleanup" {
            if (!(Test-DockerCompose)) { exit 1 }
            Remove-All
        }
        "build" {
            if (!(Test-Docker)) { exit 1 }
            if (!(Test-DockerCompose)) { exit 1 }
            Build-Images
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Unknown command: $Command"
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main 