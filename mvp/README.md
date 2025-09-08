# 🧬 Garmin Longevity Matrix MVP

**A production-ready health optimization dashboard that transforms your Garmin data into actionable longevity insights.**

## 🚀 Quick Start (Single Command!)

```bash
./start.sh
```

That's it! Your MVP will be running at:
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 What You Get

### ✅ **Core Features**
- **Real-time Garmin data sync** via background jobs
- **Biological age calculation** based on health metrics  
- **Cyberpunk dashboard** with beautiful visualizations
- **Health insights** powered by your actual data
- **Activity tracking** with detailed metrics
- **Longevity scoring** and progress tracking

### 🏗️ **Production Architecture**
```
Frontend (React) → FastAPI → PostgreSQL
                      ↓
                 Celery Worker → Redis
                      ↓
                Garmin Connect API
```

## 🛠️ Manual Setup

1. **Configure credentials** in `.env`:
   ```bash
   GARMIN_EMAIL=your_garmin_email@gmail.com
   GARMIN_PASSWORD=your_garmin_password
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Trigger initial data sync**:
   ```bash
   curl -X POST http://localhost:8000/api/sync/trigger \
     -H "Content-Type: application/json" \
     -d '{"days": 7}'
   ```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/overview` | GET | Main dashboard metrics |
| `/api/activities/recent` | GET | Recent activities |
| `/api/insights/health` | GET | AI health insights |
| `/api/sync/trigger` | POST | Trigger data sync |
| `/api/sync/status` | GET | Sync status |
| `/api/health/check` | GET | Service health check |

## 🔧 Development

```bash
# View logs
docker-compose logs -f [service_name]

# Restart specific service
docker-compose restart backend

# Run database migrations
docker-compose exec postgres psql -U postgres -d longevity

# Test Garmin connection
curl -X POST http://localhost:8000/api/test/garmin
```

## 📦 Services

- **Frontend**: Next.js React app with cyberpunk UI
- **Backend**: FastAPI with real-time health calculations
- **Database**: PostgreSQL with optimized health data schema
- **Worker**: Celery for background Garmin data extraction
- **Cache**: Redis for job queue and caching
- **Scheduler**: Celery Beat for daily automatic sync

## 🚀 Deployment

This MVP is designed for single-server deployment:

1. **Copy to server**:
   ```bash
   scp -r mvp/ user@your-server:/path/to/app/
   ```

2. **Configure domain** in docker-compose.yml

3. **Start with SSL** (add nginx-proxy or traefik)

4. **Set up monitoring** (add health checks)

## 🎯 MVP vs Full Product

**✅ MVP Includes:**
- Core Garmin data extraction
- Biological age calculation  
- Interactive dashboard
- Background job processing
- Real health insights

**🔮 Future Features:**
- Multi-user support
- Advanced ML predictions
- Integration with more wearables
- Social features & challenges
- Mobile app
- Advanced protocols tracking

## 🛠️ Troubleshooting

**Backend not starting?**
```bash
docker-compose logs backend
```

**Garmin connection failing?**
```bash
curl -X POST http://localhost:8000/api/test/garmin
```

**Database issues?**
```bash
docker-compose exec postgres psql -U postgres -d longevity -c "SELECT COUNT(*) FROM garmin.processed_daily_metrics;"
```

---

**🧬 Ship fast. Optimize health. Reach the future. 🚀**