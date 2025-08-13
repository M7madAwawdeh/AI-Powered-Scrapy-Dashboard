# 🐳 Docker Setup for AI-Powered Scrapy Dashboard

This document provides comprehensive instructions for running the AI-Powered Scrapy Dashboard using Docker containers.

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (usually included with Docker Desktop)
- **Git** for cloning the repository
- **OpenRouter API Key** for AI features

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd ai_powered_scrapy
```

### 2. Set Up Environment
```bash
# On Windows PowerShell:
.\docker\scripts\docker-setup.ps1 setup dev

# On Linux/Mac:
chmod +x docker/scripts/docker-setup.sh
./docker/scripts/docker-setup.sh setup dev
```

### 3. Configure Credentials
Edit the `.env` file with your actual credentials:
```bash
# Required: OpenRouter API Key
OPENROUTER_API_KEY=your_actual_api_key_here

# Optional: Customize other settings
DB_PASSWORD=your_custom_password
```

### 4. Start Services
```bash
# Development mode (recommended for first run)
.\docker\scripts\docker-setup.ps1 start dev

# Production mode
.\docker\scripts\docker-setup.ps1 start prod
```

### 5. Access the Dashboard
- **Dashboard**: http://localhost:8502 (dev) or http://localhost:8501 (prod)
- **pgAdmin**: http://localhost:5050 (dev only)
- **Redis Commander**: http://localhost:8081 (dev only)
- **Jupyter**: http://localhost:8888 (dev only)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80/443)│    │  PostgreSQL DB  │    │   Redis Cache   │
│   (Production)  │    │     (5432)      │    │     (6379)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Main App (8501)│
                    │  Streamlit      │
                    └─────────────────┘
```

## 📁 File Structure

```
ai_powered_scrapy/
├── Dockerfile                 # Production container
├── Dockerfile.dev            # Development container
├── docker-compose.yml        # Production services
├── docker-compose.dev.yml    # Development services
├── docker.env                # Docker environment template
├── .env                      # Your environment variables
├── docker/
│   ├── scripts/
│   │   ├── docker-setup.sh      # Linux/Mac setup script
│   │   └── docker-setup.ps1     # Windows PowerShell script
│   ├── postgres/                # Database initialization
│   ├── nginx/                   # Reverse proxy config
│   ├── prometheus/              # Monitoring config
│   └── grafana/                 # Visualization config
└── requirements.txt           # Python dependencies
```

## 🔧 Available Commands

### Setup Scripts (PowerShell)
```powershell
# Show help
.\docker\scripts\docker-setup.ps1 help

# Set up development environment
.\docker\scripts\docker-setup.ps1 setup dev

# Set up production environment
.\docker\scripts\docker-setup.ps1 setup prod

# Start services
.\docker\scripts\docker-setup.ps1 start dev
.\docker\scripts\docker-setup.ps1 start prod

# Stop services
.\docker\scripts\docker-setup.ps1 stop dev
.\docker\scripts\docker-setup.ps1 stop prod

# View logs
.\docker\scripts\docker-setup.ps1 logs dev
.\docker\scripts\docker-setup.ps1 logs prod

# Check status
.\docker\scripts\docker-setup.ps1 status dev
.\docker\scripts\docker-setup.ps1 status prod

# Clean up everything
.\docker\scripts\docker-setup.ps1 cleanup dev
.\docker\scripts\docker-setup.ps1 cleanup prod
```

### Setup Scripts (Bash)
```bash
# Show help
./docker/scripts/docker-setup.sh help

# Set up development environment
./docker/scripts/docker-setup.sh setup dev

# Set up production environment
./docker/scripts/docker-setup.sh setup prod

# Start services
./docker/scripts/docker-setup.sh start dev
./docker/scripts/docker-setup.sh start prod

# Stop services
./docker/scripts/docker-setup.sh stop dev
./docker/scripts/docker-setup.sh stop prod

# View logs
./docker/scripts/docker-setup.sh logs dev
./docker/scripts/docker-setup.sh logs prod

# Check status
./docker/scripts/docker-setup.sh status dev
./docker/scripts/docker-setup.sh status prod

# Clean up everything
./docker/scripts/docker-setup.sh cleanup dev
./docker/scripts/docker-setup.sh cleanup prod
```

## 🌍 Environment Modes

### Development Mode (`docker-compose.dev.yml`)
- **Ports**: 8502 (dashboard), 5050 (pgAdmin), 8081 (Redis), 8888 (Jupyter)
- **Features**: Live code reloading, debugging tools, development databases
- **Use Case**: Development, testing, debugging

### Production Mode (`docker-compose.yml`)
- **Ports**: 8501 (dashboard), 80/443 (nginx), 9090 (Prometheus), 3000 (Grafana)
- **Features**: Optimized performance, monitoring, reverse proxy
- **Use Case**: Production deployment, staging environments

## 🔐 Environment Variables

### Required Variables
```bash
# OpenRouter API for AI features
OPENROUTER_API_KEY=your_api_key_here

# Database connection
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ai_scrapy_dashboard
DB_USER=postgres
DB_PASSWORD=your_password
```

### Optional Variables
```bash
# AI Model Configuration
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7

# Scraping Configuration
SCRAPING_DELAY=2
SCRAPING_TIMEOUT=30
SCRAPING_RETRY_TIMES=3

# Dashboard Configuration
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0
LOG_LEVEL=INFO
```

## 🚀 Deployment Options

### Local Development
```bash
# Quick start for development
.\docker\scripts\docker-setup.ps1 setup dev
.\docker\scripts\docker-setup.ps1 start dev
```

### Production Deployment
```bash
# Production setup
.\docker\scripts\docker-setup.ps1 setup prod
.\docker\scripts\docker-setup.ps1 start prod
```

### Cloud Deployment
```bash
# Build and push to registry
docker build -t your-registry/ai-scrapy-dashboard:latest .
docker push your-registry/ai-scrapy-dashboard:latest

# Deploy with custom compose file
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring & Logs

### View Logs
```bash
# All services
.\docker\scripts\docker-setup.ps1 logs dev

# Specific service
docker-compose -f docker-compose.dev.yml logs -f app

# Database logs
docker-compose -f docker-compose.dev.yml logs -f postgres
```

### Health Checks
```bash
# Check service status
.\docker\scripts\docker-setup.ps1 status dev

# Manual health check
docker-compose -f docker-compose.dev.yml ps
```

### Monitoring (Production)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8501

# Kill the process or use different ports
# Edit docker-compose.yml to change ports
```

#### 2. Docker Not Running
```bash
# Start Docker Desktop
# Wait for it to fully start
# Then run your commands
```

#### 3. Permission Denied
```bash
# On Windows, run PowerShell as Administrator
# On Linux/Mac, use sudo if needed
```

#### 4. Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Check logs
docker-compose -f docker-compose.dev.yml logs postgres

# Restart the service
docker-compose -f docker-compose.dev.yml restart postgres
```

### Debug Mode
```bash
# Run with verbose output
docker-compose -f docker-compose.dev.yml up --verbose

# Check container logs
docker logs ai_scrapy_app_dev

# Enter container for debugging
docker exec -it ai_scrapy_app_dev bash
```

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
# Rebuild images with latest dependencies
.\docker\scripts\docker-setup.ps1 build dev

# Restart services
.\docker\scripts\docker-setup.ps1 restart dev
```

### Backup and Restore
```bash
# Backup database
docker exec ai_scrapy_postgres_dev pg_dump -U postgres ai_scrapy_dashboard_dev > backup.sql

# Restore database
docker exec -i ai_scrapy_postgres_dev psql -U postgres ai_scrapy_dashboard_dev < backup.sql
```

### Clean Up
```bash
# Remove all containers and volumes
.\docker\scripts\docker-setup.ps1 cleanup dev

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

## 📚 Additional Resources

### Docker Commands Reference
```bash
# List containers
docker ps -a

# List images
docker images

# List volumes
docker volume ls

# List networks
docker network ls

# System info
docker system df
```

### Docker Compose Commands
```bash
# Scale services
docker-compose -f docker-compose.dev.yml up -d --scale app=3

# View service logs
docker-compose -f docker-compose.dev.yml logs app

# Execute commands in running containers
docker-compose -f docker-compose.dev.yml exec app python manage.py shell
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs**: `.\docker\scripts\docker-setup.ps1 logs dev`
2. **Verify Docker is running**: `docker info`
3. **Check service status**: `.\docker\scripts\docker-setup.ps1 status dev`
4. **Review this documentation**
5. **Check the main README.md** for general project information

## 🎯 Next Steps

After successful Docker setup:

1. **Access the dashboard** at http://localhost:8502 (dev) or http://localhost:8501 (prod)
2. **Run the pipeline**: Use the dashboard or run `python run_pipeline.py --full`
3. **Explore AI features**: Test categorization and description generation
4. **Customize scraping**: Modify spider configurations
5. **Scale up**: Add more workers or services as needed

---

**Happy Scraping! 🕷️✨** 