#!/bin/bash

# Deployment script for Inventory Management System
set -e

echo "=================================="
echo "Inventory System Deployment Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env.production exists
if [ ! -f "./backend/.env.production" ]; then
    echo -e "${RED}Error: .env.production file not found!${NC}"
    echo "Please copy .env.production.example to .env.production and configure it."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
echo "Checking required tools..."
if ! command_exists docker; then
    echo -e "${RED}Error: Docker is not installed!${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}Error: Docker Compose is not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Ask for deployment mode
echo "Select deployment mode:"
echo "1) Production (recommended)"
echo "2) Development"
read -p "Enter your choice [1]: " choice
choice=${choice:-1}

if [ "$choice" = "1" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    echo -e "${GREEN}Deploying in PRODUCTION mode${NC}"
else
    COMPOSE_FILE="docker-compose.yml"
    echo -e "${YELLOW}Deploying in DEVELOPMENT mode${NC}"
fi

echo ""

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    echo "Pulling latest changes from git..."
    git pull || echo -e "${YELLOW}Warning: Could not pull from git${NC}"
    echo ""
fi

# Backup database (if exists)
echo "Creating database backup..."
mkdir -p ./backups
BACKUP_FILE="./backups/backup_$(date +%Y%m%d_%H%M%S).sql"

if docker ps | grep -q "inventory_db"; then
    docker exec inventory_db pg_dump -U inventory_user inventory_db > "$BACKUP_FILE" 2>/dev/null || echo -e "${YELLOW}No existing database to backup${NC}"
    if [ -f "$BACKUP_FILE" ]; then
        echo -e "${GREEN}✓ Database backed up to $BACKUP_FILE${NC}"
    fi
else
    echo -e "${YELLOW}No running database container found, skipping backup${NC}"
fi
echo ""

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down || true
echo ""

# Build and start containers
echo "Building and starting containers..."
docker-compose -f $COMPOSE_FILE build --no-cache
docker-compose -f $COMPOSE_FILE up -d

echo ""
echo "Waiting for services to start..."
sleep 10

# Check if containers are running
if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Containers are running${NC}"
else
    echo -e "${RED}Error: Containers failed to start!${NC}"
    docker-compose -f $COMPOSE_FILE logs
    exit 1
fi

echo ""
echo "Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate

echo ""
echo "Collecting static files..."
docker-compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

echo ""
echo "=================================="
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo "=================================="
echo ""
echo "Services are running on:"
echo "  - Frontend: http://localhost"
echo "  - Backend API: http://localhost/api"
echo "  - Admin Panel: http://localhost/admin"
echo ""
echo "To view logs:"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""
