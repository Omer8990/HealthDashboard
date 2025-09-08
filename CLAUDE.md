# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Garmin Longevity Matrix** - a production-ready health optimization dashboard that transforms Garmin health metrics into actionable longevity insights. Originally a complex data engineering learning project, it has evolved into a clean MVP serving real customers.

## Architecture

The codebase follows a simple, scalable architecture:

```
Garmin Connect API → Celery Worker → PostgreSQL → FastAPI → Dashboard (HTML/JS)
                         ↓
                    Redis Queue
```

### Key Components

1. **MVP Application** (`mvp/`)
   - `backend/main.py`: FastAPI application with health endpoints
   - `backend/tasks.py`: Celery background tasks for Garmin data extraction
   - `frontend/index.html`: Simple HTML dashboard with JavaScript
   - `database/init.sql`: PostgreSQL schema for health data
   - `docker-compose.yml`: Service orchestration

2. **Backend API** (`mvp/backend/`)
   - FastAPI with CORS middleware for dashboard communication
   - Health metrics calculation and biological age algorithms
   - Background job management with Celery
   - PostgreSQL integration with SQLAlchemy

3. **Frontend Dashboard** (`mvp/frontend/`)
   - Static HTML with cyberpunk theme
   - Real-time API integration with dashboard metrics
   - Responsive design for health data visualization
   - Nginx serving for production deployment

4. **Background Processing** (`mvp/backend/tasks.py`)
   - Celery tasks for Garmin Connect data extraction
   - Automated daily sync scheduling with Celery Beat
   - Data processing and biological age calculation
   - Health insights generation

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL (handled by Docker)

### Environment Setup
1. Copy `mvp/.env.example` to `mvp/.env` and configure:
   - `GARMIN_EMAIL`: Your Garmin Connect email
   - `GARMIN_PASSWORD`: Your Garmin Connect password
   - `DATABASE_URL`: PostgreSQL connection string (pre-configured for Docker)
   - `REDIS_URL`: Redis connection string (pre-configured for Docker)

### Quick Start
```bash
cd mvp
./start.sh
```

### Services
All services run in Docker containers:
```bash
cd mvp
docker-compose up -d
```

## Key Data Models

The system tracks longevity-focused metrics:
- **Biological Age Calculation**: Multi-factor algorithm based on resting heart rate, activity levels, and health patterns
- **Activity Tracking**: Running, cycling, walking with heart rate zones and performance metrics
- **Health Insights**: AI-powered recommendations based on real data patterns
- **Gamification**: XP system, levels, achievements, and streak tracking

## Access Points
- Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (postgres/postgres)
- Redis: localhost:6379

## Code Patterns

### FastAPI Backend
- Uses Pydantic models for request/response validation
- SQLAlchemy for database operations with direct SQL for complex queries
- CORS middleware for frontend communication
- Celery integration for background tasks

### Frontend JavaScript
- Vanilla JavaScript with fetch API for backend communication
- Real-time dashboard updates every 30 seconds
- Cyberpunk styling with CSS animations
- Responsive design for mobile and desktop

### Celery Tasks
- Background data extraction from Garmin Connect
- Retry logic with exponential backoff
- Daily automated sync with Celery Beat
- Health metrics processing and storage

### Database Schema
- `garmin.staging_activities`: Raw activity data from Garmin
- `garmin.processed_daily_metrics`: Calculated daily health metrics
- Indexes optimized for date-based queries
- PostgreSQL functions for biological age calculation

## Testing

Test the MVP with these commands:
```bash
# Health check
curl http://localhost:8000/api/health/check

# Dashboard data
curl http://localhost:8000/api/dashboard/overview

# Trigger sync
curl -X POST http://localhost:8000/api/sync/trigger -d '{"days": 1}'
```

## Architecture Evolution

This project evolved from a complex Airflow/Spark pipeline into a clean MVP:
- **Removed**: Airflow, Spark, complex orchestration
- **Added**: Simple Celery workers, direct FastAPI endpoints
- **Kept**: PostgreSQL, health calculations, dashboard concept
- **Improved**: Deployment simplicity, development speed, maintainability