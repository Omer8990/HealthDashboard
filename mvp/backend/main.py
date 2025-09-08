"""
Garmin Longevity Matrix MVP - FastAPI Backend
Simple, production-ready API for health data dashboard
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import logging

# Import Celery tasks
from tasks import extract_daily_data, extract_historical_data, test_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Garmin Longevity Matrix API",
    description="🧬 MVP API for cyberpunk health optimization dashboard",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/longevity")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class DashboardMetrics(BaseModel):
    current_bio_age: float
    aging_velocity: float
    longevity_score: int
    years_gained: float
    streak_days: int
    level: int
    xp: int

class Activity(BaseModel):
    activity_type: str
    activity_name: str
    start_time: str
    duration_minutes: float
    distance_km: float
    calories: int
    avg_heart_rate: int
    max_heart_rate: int

class Insight(BaseModel):
    type: str
    title: str
    message: str
    impact: str
    icon: str

class SyncRequest(BaseModel):
    days: Optional[int] = 1

@app.get("/")
async def root():
    return {
        "message": "🧬 Garmin Longevity Matrix MVP API",
        "status": "online",
        "version": "1.0.0",
        "description": "Production-ready health optimization dashboard"
    }

@app.get("/api/dashboard/overview", response_model=DashboardMetrics)
async def get_dashboard_overview():
    """Get main dashboard metrics"""
    try:
        with engine.connect() as conn:
            # Get latest metrics
            result = conn.execute(text("""
                SELECT 
                    biological_age,
                    longevity_score,
                    resting_heart_rate,
                    activities_count,
                    total_steps,
                    total_distance_km,
                    processed_at
                FROM garmin.processed_daily_metrics 
                ORDER BY date DESC 
                LIMIT 1
            """)).fetchone()
            
            if result:
                bio_age, longevity_score, rhr, activities, steps, distance, processed_at = result
                
                # Calculate derived metrics
                chronological_age = 25  # Configure this per user later
                aging_velocity = ((bio_age - chronological_age) / chronological_age) if bio_age else 0
                years_gained = chronological_age - bio_age if bio_age else 0
                
                # Calculate activity streak (simplified)
                streak_result = conn.execute(text("""
                    SELECT COUNT(*) as streak
                    FROM garmin.processed_daily_metrics 
                    WHERE activities_count > 0
                """)).fetchone()
                
                streak_days = streak_result[0] if streak_result else 0
                
                # Calculate level and XP
                total_activities = conn.execute(text("""
                    SELECT SUM(activities_count), SUM(total_distance_km)
                    FROM garmin.processed_daily_metrics
                """)).fetchone()
                
                activity_count, total_dist = total_activities or (0, 0)
                xp = int((activity_count or 0) * 100 + (total_dist or 0) * 10)
                level = max(1, xp // 1000)
                
                return DashboardMetrics(
                    current_bio_age=float(bio_age) if bio_age else 25.0,
                    aging_velocity=aging_velocity,
                    longevity_score=int(longevity_score) if longevity_score else 80,
                    years_gained=years_gained,
                    streak_days=streak_days,
                    level=level,
                    xp=xp
                )
            else:
                # Return default values if no data
                return DashboardMetrics(
                    current_bio_age=25.0,
                    aging_velocity=0.0,
                    longevity_score=80,
                    years_gained=0.0,
                    streak_days=0,
                    level=1,
                    xp=0
                )
                
    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activities/recent")
async def get_recent_activities(limit: int = 10):
    """Get recent activities"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    activity_type,
                    activity_name,
                    start_time,
                    duration_seconds / 60.0 as duration_minutes,
                    distance_meters / 1000.0 as distance_km,
                    calories,
                    avg_heart_rate,
                    max_heart_rate
                FROM garmin.staging_activities
                ORDER BY start_time DESC
                LIMIT :limit
            """), {"limit": limit}).fetchall()
            
            activities = []
            for row in result:
                activities.append({
                    "activity_type": row[0] or "unknown",
                    "activity_name": row[1] or "Activity",
                    "start_time": row[2].isoformat() if row[2] else "",
                    "duration_minutes": float(row[3]) if row[3] else 0,
                    "distance_km": float(row[4]) if row[4] else 0,
                    "calories": int(row[5]) if row[5] else 0,
                    "avg_heart_rate": int(row[6]) if row[6] else 0,
                    "max_heart_rate": int(row[7]) if row[7] else 0
                })
            
            return {"activities": activities}
            
    except Exception as e:
        logger.error(f"Recent activities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/health")
async def get_health_insights():
    """Get AI-powered health insights"""
    try:
        with engine.connect() as conn:
            # Get latest metrics
            result = conn.execute(text("""
                SELECT 
                    resting_heart_rate,
                    total_steps,
                    activities_count,
                    biological_age,
                    longevity_score
                FROM garmin.processed_daily_metrics
                ORDER BY date DESC LIMIT 1
            """)).fetchone()
            
            insights = []
            
            if result:
                rhr, steps, activities, bio_age, longevity_score = result
                
                # Generate insights based on real data
                if rhr and rhr <= 55:
                    insights.append({
                        "type": "achievement",
                        "title": "Elite Cardiovascular Fitness",
                        "message": f"Your resting heart rate of {rhr} bpm indicates exceptional cardiovascular health.",
                        "impact": "+2.5 years life expectancy",
                        "icon": "❤️"
                    })
                
                if bio_age and bio_age < 25:
                    insights.append({
                        "type": "success",
                        "title": "Biological Age Advantage",
                        "message": f"Your biological age ({bio_age:.1f}) shows excellent health optimization!",
                        "impact": f"+{25 - bio_age:.1f} years gained",
                        "icon": "🧬"
                    })
                
                if activities and activities > 0:
                    insights.append({
                        "type": "success",
                        "title": "Active Lifestyle",
                        "message": f"Staying consistent with {activities} activities recently.",
                        "impact": "+1.2 years life expectancy",
                        "icon": "🏃"
                    })
                
                if longevity_score and longevity_score >= 90:
                    insights.append({
                        "type": "achievement",
                        "title": "Longevity Master",
                        "message": f"Your longevity score of {longevity_score}/100 puts you in the top 5%!",
                        "impact": "Maximum optimization achieved",
                        "icon": "🏆"
                    })
            
            # Add default insights if no data
            if not insights:
                insights = [
                    {
                        "type": "recommendation",
                        "title": "Start Your Journey",
                        "message": "Connect your Garmin device to begin tracking your longevity metrics.",
                        "impact": "Begin optimization",
                        "icon": "🚀"
                    }
                ]
            
            return {"insights": insights}
            
    except Exception as e:
        logger.error(f"Health insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sync/trigger")
async def trigger_sync(request: SyncRequest):
    """Trigger Garmin data synchronization"""
    try:
        if request.days == 1:
            # Single day sync
            task = extract_daily_data.delay()
        else:
            # Historical sync
            task = extract_historical_data.delay(request.days)
        
        return {
            "message": f"Sync triggered for {request.days} day(s)",
            "task_id": task.id,
            "status": "queued"
        }
        
    except Exception as e:
        logger.error(f"Sync trigger error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sync/status")
async def get_sync_status():
    """Get synchronization status"""
    try:
        with engine.connect() as conn:
            # Get latest sync info
            result = conn.execute(text("""
                SELECT 
                    MAX(processed_at) as last_sync,
                    COUNT(*) as total_days
                FROM garmin.processed_daily_metrics
            """)).fetchone()
            
            last_sync, total_days = result or (None, 0)
            
            return {
                "last_sync": last_sync.isoformat() if last_sync else None,
                "total_days": total_days,
                "status": "active" if total_days > 0 else "pending"
            }
            
    except Exception as e:
        logger.error(f"Sync status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health/check")
async def health_check():
    """Health check endpoint"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/test/garmin")
async def test_garmin_connection():
    """Test Garmin Connect connection"""
    try:
        task = test_connection.delay()
        return {
            "message": "Testing Garmin connection...",
            "task_id": task.id,
            "status": "testing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract/daily")
async def trigger_daily_extraction():
    """Trigger daily data extraction from Garmin"""
    try:
        task = extract_daily_data.delay()
        return {
            "message": "Starting daily data extraction...",
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract/historical")
async def trigger_historical_extraction(days: int = 7):
    """Trigger historical data extraction from Garmin"""
    try:
        task = extract_historical_data.delay(days)
        return {
            "message": f"Starting historical data extraction for {days} days...",
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)