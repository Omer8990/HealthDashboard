# 🧬 Garmin Longevity Matrix Pipeline

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![Spark](https://img.shields.io/badge/Apache_Spark-3.0+-orange.svg)](https://spark.apache.org/)
[![Airflow](https://img.shields.io/badge/Apache_Airflow-2.0+-green.svg)](https://airflow.apache.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **A cyberpunk-themed health data pipeline that gamifies longevity and anti-aging protocols, transforming your Garmin health metrics into an interactive command center for maximizing healthspan and reaching the singularity.**

<p align="center">
  <img src="https://img.shields.io/badge/HACK_AGING-REACH_2077-00ffff?style=for-the-badge&labelColor=8800ff" alt="Hack Aging">
</p>

## 🚀 Quick Start Guide

### Prerequisites
- **Docker & Docker Compose** (for containerized services)
- **Node.js 16+** (for frontend development)
- **Python 3.9+** (optional, for local development)
- **Garmin Connect account** (for data extraction)

### 🎯 One-Command Setup

The easiest way to start the entire pipeline:

```bash
# 1. Clone the repository
git clone https://github.com/Omer8990/HealthDashboard.git
cd HealthDashboard

# 2. Navigate to the pipeline directory
cd garmin-health-pipeline

# 3. Start all core services (one command!)
docker-compose up -d

# 4. Start dashboard services
docker-compose --profile dashboard up -d

# 5. Start frontend in development mode (in a new terminal)
cd dashboard/frontend
npm install
npm run dev
```

**That's it!** 🎉 Your services will be running at:
- **Dashboard**: http://localhost:3000
- **Airflow**: http://localhost:8080 (admin/admin)
- **Backend API**: http://localhost:8000
- **Spark UI**: http://localhost:8081
- **PostgreSQL**: localhost:5432

### ⚡ Service Status Check

After starting, verify all services are running:

```bash
# Check all container status
docker-compose ps

# Test endpoints
curl http://localhost:3000                    # Frontend
curl http://localhost:8000/api/insights/health # Backend API
curl http://localhost:8080/health             # Airflow
curl http://localhost:8081                    # Spark UI
```

## 🔧 Detailed Setup (For Development)

### 1. Environment Configuration

Create your environment file:
```bash
cp .env.example .env
```

Configure the following variables:
```env
# Garmin Connect Credentials
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_secure_password

# Database Connection
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/longevity

# Airflow Configuration
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# Optional: External database
# DATABASE_URL=postgresql://user:pass@localhost:5432/longevity
```

### 2. Service Architecture

```mermaid
graph TB
    A[🚀 docker-compose up -d] --> B[PostgreSQL Database]
    A --> C[Redis Cache]
    A --> D[Apache Spark Cluster]
    A --> E[Apache Airflow]
    
    F[🌐 --profile dashboard] --> G[Backend API :8000]
    F --> H[Frontend Container*]
    
    I[🛠️ npm run dev] --> J[Frontend Dev Server :3000]
    
    B --> G
    C --> E
    D --> E
    E --> B
    G --> J
    
    style A fill:#00ffff
    style F fill:#ff00ff
    style I fill:#ffff00
    style J fill:#00ff00
```

*Note: Frontend container has build issues, so we use dev mode*

### 3. Complete Service Startup Order

```bash
# Step 1: Start core infrastructure
docker-compose up -d
# ✅ Starts: PostgreSQL, Redis, Spark, Airflow

# Step 2: Wait for services to be healthy (30-60 seconds)
docker-compose ps  # Check all services are "healthy"

# Step 3: Start dashboard backend
docker-compose --profile dashboard up -d dashboard-backend
# ✅ Starts: Backend API at :8000

# Step 4: Start frontend (dev mode - recommended)
cd dashboard/frontend
npm install  # Only needed first time
npm run dev  # Starts at :3000
```

### 4. Database Initialization

The database is automatically initialized with:
- ✅ PostgreSQL with `longevity` database
- ✅ Garmin schema with staging and processed tables
- ✅ Health insights table (for Airflow DAGs)
- ✅ All required extensions and indexes

Check database status:
```bash
# Connect to database
docker exec -it garmin-health-pipeline-postgres-1 psql -U postgres -d longevity

# List tables
\dt garmin.*

# Check health insights table
SELECT * FROM garmin.health_insights LIMIT 5;
```

## 🎮 Using the Dashboard

### Access Points
- **Main Dashboard**: http://localhost:3000
  - Cyberpunk-themed health metrics
  - Biological age calculation
  - Longevity protocols tracking
  - Achievement system

- **Airflow UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
  - DAG management and monitoring

- **Backend API**: http://localhost:8000
  - RESTful endpoints
  - Health insights: `/api/insights/health`
  - Activities: `/api/activities/detailed`

### Key Features Working
✅ **Frontend**: Cyberpunk dashboard with real-time data  
✅ **Backend API**: Health insights and achievements  
✅ **Database**: PostgreSQL with full schema  
✅ **Airflow**: DAG orchestration (with health_insights table)  
✅ **Spark**: Distributed processing cluster  
✅ **Data Flow**: Complete pipeline architecture  

## 🛠️ Development Workflow

### Making Changes

```bash
# Backend changes
cd dashboard/backend
# Edit Python files - changes auto-reload with uvicorn

# Frontend changes  
cd dashboard/frontend
# Edit React/TypeScript files - hot reload with Next.js

# Airflow DAGs
cd airflow/dags
# Edit Python files - Airflow picks up changes automatically

# Database changes
docker exec -it garmin-health-pipeline-postgres-1 psql -U postgres -d longevity
# Run SQL commands directly
```

### Restarting Services

```bash
# Restart specific service
docker-compose restart dashboard-backend

# Restart all services
docker-compose down && docker-compose up -d

# Reset everything (nuclear option)
docker-compose down -v  # Removes volumes too
docker-compose up -d
```

## 🐛 Troubleshooting

### Common Issues

1. **Frontend build errors**
   ```bash
   # Solution: Use dev mode instead of Docker
   cd dashboard/frontend
   npm run dev
   ```

2. **Airflow DAG failures**
   ```bash
   # Check logs
   docker logs garmin-health-pipeline-airflow-scheduler-1
   
   # Verify health_insights table exists
   docker exec garmin-health-pipeline-postgres-1 psql -U postgres -d longevity -c "SELECT * FROM garmin.health_insights;"
   ```

3. **Database connection issues**
   ```bash
   # Check PostgreSQL is running
   docker ps | grep postgres
   
   # Test connection
   docker exec garmin-health-pipeline-postgres-1 psql -U postgres -l
   ```

4. **Spark not working**
   ```bash
   # Check Spark UI
   curl http://localhost:8081
   
   # Check workers
   docker logs garmin-health-pipeline-spark-worker-1-1
   ```

### Port Conflicts

If ports are already in use:
- Frontend: Change in `package.json` → `"dev": "next dev -p 3001"`
- Backend: Change in `docker-compose.yml` → `"8001:8000"`
- Airflow: Change in `docker-compose.yml` → `"8082:8080"`

### Performance Tips

- **Memory**: Ensure Docker has at least 4GB RAM allocated
- **CPU**: 4+ cores recommended for Spark processing
- **Disk**: At least 10GB free space for containers and data

## 📊 API Documentation

### Backend Endpoints

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/insights/health` | GET | Health insights and achievements | ✅ Working |
| `/api/activities/detailed` | GET | Detailed activity analysis | ⚠️ Needs data |
| `/api/health/trends` | GET | Health trend analysis | ⚠️ Needs data |
| `/api/biomarkers` | GET | Latest biomarker values | 🔄 TODO |
| `/api/biological-age` | GET | Biological age calculation | 🔄 TODO |

### Health Insights Response Example
```json
{
  "insights": [
    {
      "type": "achievement",
      "title": "Elite Cardiovascular Fitness", 
      "message": "Your resting heart rate of 47 bpm is in the elite athlete range.",
      "impact": "+2.5 years life expectancy",
      "icon": "❤️"
    },
    {
      "type": "success",
      "title": "Biological Age Advantage",
      "message": "Your biological age (18.5) is 3.5 years younger than your chronological age!",
      "impact": "+3.5 years gained", 
      "icon": "🧬"
    }
  ]
}
```

## 🔮 Architecture Deep Dive

### Data Flow
```
Garmin Connect → Extract → PostgreSQL → Spark → Process → Airflow → Dashboard
```

### Container Architecture
```
┌─ Core Services (docker-compose up -d) ─┐
│  ├── PostgreSQL (Database)              │
│  ├── Redis (Cache/Queue)                │ 
│  ├── Spark Master + 2 Workers           │
│  ├── Airflow (Scheduler/Webserver)      │
│  └── Airflow (Worker/Triggerer)         │
└─────────────────────────────────────────┘
┌─ Dashboard (--profile dashboard) ───────┐
│  ├── Backend API (FastAPI)              │
│  └── Frontend (Next.js) - Use dev mode  │
└─────────────────────────────────────────┘
```

### Health Check Commands
```bash
# All services status
docker-compose ps

# Individual health checks
curl -f http://localhost:3000 || echo "Frontend down"
curl -f http://localhost:8000/api/insights/health || echo "Backend down"  
curl -f http://localhost:8080/health || echo "Airflow down"
curl -f http://localhost:8081 || echo "Spark down"
```

---

## 🚀 Production Deployment

For production deployment, see [`DEPLOYMENT.md`](DEPLOYMENT.md) for:
- Docker Swarm setup
- Kubernetes manifests
- Environment variable security
- SSL/TLS configuration
- Performance tuning
- Monitoring setup

---

<p align="center">
  <strong>🧬 Hack your biology. Reverse your age. Reach the future. 🚀</strong>
</p>

<p align="center">
  Built with 💜 for the longevity community
</p>