# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Garmin Longevity Matrix Pipeline** - a cyberpunk-themed health data pipeline that transforms Garmin health metrics into a gamified anti-aging optimization platform. The system extracts data from Garmin Connect, processes it through Apache Spark, orchestrates workflows with Apache Airflow, and presents insights through an interactive dashboard.

## Architecture

The codebase follows a multi-component data pipeline architecture:

```
Garmin Connect API → Data Extraction → PostgreSQL → Apache Spark → Processed Data
                                                            ↓
Dashboard (React/Next.js) ← REST API ← Materialized Views ← Apache Airflow
```

### Key Components

1. **Data Extraction** (`garmin-health-pipeline/extraction/`)
   - `garmin_extractor.py`: Main extraction logic using garminconnect library
   - Handles authentication, rate limiting, and data retrieval
   - Uses SQLAlchemy for database operations

2. **Data Processing** (`garmin-health-pipeline/spark/`)
   - PySpark jobs for complex calculations
   - `jobs/`: Contains processing scripts for activities and metrics
   - Biological age algorithms and protocol scoring

3. **Orchestration** (`garmin-health-pipeline/airflow/`)
   - `dags/`: Contains workflow definitions
   - `garmin_daily_sync.py`: Daily automated data sync
   - `garmin_historical_load.py`: Historical data backfilling

4. **Database** (`garmin-health-pipeline/database/`)
   - `models.py`: Database schema definitions
   - PostgreSQL-based data storage with staging and processed tables

5. **Dashboard** (`garmin-health-pipeline/dashboard/`)
   - `frontend/`: React/Next.js application
   - `backend/`: API server for dashboard data

6. **Configuration** (`garmin-health-pipeline/config/`)
   - Environment configuration and settings
   - `.env.example`: Template for required environment variables

## Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Apache Spark 3.0+
- Apache Airflow 2.0+
- Node.js 16+ (for dashboard)
- Docker & Docker Compose

### Environment Setup
1. Copy `garmin-health-pipeline/config/.env.example` to `.env` and configure:
   - `GARMIN_EMAIL`: Your Garmin Connect email
   - `GARMIN_PASSWORD`: Your Garmin Connect password
   - `DATABASE_URL`: PostgreSQL connection string
   - `AIRFLOW_HOME`: Path to Airflow installation
   - `SPARK_HOME`: Path to Spark installation

### Database Initialization
```bash
psql -U postgres -c "CREATE DATABASE longevity;"
psql -U postgres -d longevity -f garmin-health-pipeline/database/init.sql
```

### Python Dependencies
Install dependencies from `garmin-health-pipeline/extraction/requirements.txt` and other component requirements.

### Services
Use Docker Compose for service orchestration:
```bash
cd garmin-health-pipeline
docker-compose up -d
```

### Airflow Setup
```bash
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
airflow webserver -D
airflow scheduler -D
```

### Dashboard Development
```bash
cd garmin-health-pipeline/dashboard
npm install
npm run dev
```

## Key Data Models

The system tracks longevity-focused metrics:
- **Biological Age Calculation**: Multi-factor algorithm based on VO2 Max (30%), HRV (20%), Sleep Quality (20%), Body Composition (15%), Stress (15%)
- **Protocol Tracking**: Zone 2 training, HIIT, time-restricted feeding, sleep optimization, cold/heat therapy
- **Gamification**: XP system, achievements, leaderboards based on protocol adherence

## Access Points
- Dashboard: http://localhost:3000
- Airflow UI: http://localhost:8080
- PostgreSQL: localhost:5432

## Code Patterns

### Data Extraction
- Uses `garminconnect` library for API access
- Implements retry logic with `@retry` decorator
- Configuration managed through dataclasses
- Database operations use SQLAlchemy

### Airflow DAGs
- Daily sync at 6:00 AM with sequential processing steps
- Uses TaskGroups for organized workflow structure
- PostgresOperator and SparkSubmitOperator for data operations

### Spark Processing
- PySpark for distributed data processing
- Focus on biological age calculations and protocol scoring
- Custom algorithms for longevity metrics

## Testing

The project includes a `tests/` directory structure. Test execution should be determined by examining existing test files and patterns in the repository.