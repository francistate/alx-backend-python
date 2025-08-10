# Docker Setup for Messaging App

This project has been containerized using Docker and Docker Compose for easy deployment and development.

## Files Created

1. **Dockerfile** - Containerizes the Django application
2. **docker-compose.yml** - Orchestrates multi-container setup with web and database services
3. **requirements.txt** - Lists all Python dependencies
4. **.env** - Contains environment variables (not committed to git)
5. **.dockerignore** - Excludes unnecessary files from Docker build context

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## Setup Instructions

### 1. Build and Run with Docker Compose

```bash
# Navigate to the messaging_app directory
cd messaging_app

# Build and start all services
docker-compose up --build

# To run in detached mode (background)
docker-compose up -d --build
```

### 2. The setup includes:

- **Web Service**: Django application running on port 8000
- **Database Service**: MySQL 8.0 running on port 3306
- **Data Persistence**: MySQL data is stored in a Docker volume

### 3. Access the Application

- Application: http://localhost:8000
- MySQL Database: localhost:3306

### 4. Environment Variables

The `.env` file contains:
- Database connection settings
- Django configuration
- Secret keys and passwords

### 5. Useful Docker Commands

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs
docker-compose logs web  # for web service only
docker-compose logs db   # for database service only

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: This will delete database data)
docker-compose down -v

# Execute commands in running containers
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Rebuild containers
docker-compose build
docker-compose up --build
```

### 6. Database Migrations

The docker-compose.yml is configured to run migrations automatically when the web container starts. However, you can also run them manually:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### 7. Development Workflow

For development, the current directory is mounted as a volume, so code changes are reflected immediately without rebuilding the container.

## Notes

- The MySQL database data persists between container restarts using Docker volumes
- Environment variables are loaded from the .env file (not tracked in git for security)
- The setup follows Docker best practices including multi-stage builds, non-root user, and proper health checks