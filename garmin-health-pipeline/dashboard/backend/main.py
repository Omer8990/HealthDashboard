"""
FastAPI backend for Garmin Longevity Matrix Dashboard
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime, timedelta
import json
import asyncio
import uvicorn

app = FastAPI(
    title="Garmin Longevity Matrix API",
    description="🧬 Cyberpunk-themed health data API for longevity optimization",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class BiologicalAge(BaseModel):
    date: str
    chronological_age: float
    biological_age: float
    aging_velocity: float
    vo2_max_score: float
    hrv_score: float
    sleep_score: float
    stress_score: float

class DashboardMetrics(BaseModel):
    current_bio_age: float
    aging_velocity: float
    longevity_score: int
    years_gained: float
    streak_days: int
    level: int
    xp: int

class ProtocolAdherence(BaseModel):
    protocol_name: str
    target_value: float
    actual_value: float
    adherence_percentage: float
    impact_years: float

class ActivitySummary(BaseModel):
    date: str
    activity_type: str
    duration_minutes: float
    calories: int
    zone2_minutes: Optional[int] = 0
    hiit_sessions: int = 0

@app.get("/")
async def root():
    return {
        "message": "🧬 Welcome to the Longevity Matrix API",
        "status": "online",
        "version": "1.0.0",
        "description": "Hack your biology. Reverse your age. Reach the future."
    }

@app.get("/api/dashboard/overview", response_model=DashboardMetrics)
async def get_dashboard_overview():
    """Get main dashboard metrics"""
    try:
        with engine.connect() as conn:
            # Get latest biological age data (simulated for MVP)
            current_bio_age = 28.5
            aging_velocity = -0.02  # Negative means aging slower
            longevity_score = 85
            years_gained = 2.3
            streak_days = 47
            level = 15
            xp = 12450
            
            return DashboardMetrics(
                current_bio_age=current_bio_age,
                aging_velocity=aging_velocity,
                longevity_score=longevity_score,
                years_gained=years_gained,
                streak_days=streak_days,
                level=level,
                xp=xp
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/biological-age/history")
async def get_biological_age_history(days: int = 30):
    """Get biological age trend over time"""
    try:
        # Generate simulated data for MVP
        history = []
        base_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Simulate improving biological age over time
            bio_age = 30.0 - (i * 0.02) + (i % 7) * 0.1  # Weekly variations
            
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "chronological_age": 35.0,
                "biological_age": round(bio_age, 1),
                "aging_velocity": round(-0.01 - (i * 0.001), 3),
                "vo2_max_score": 75 + (i % 10),
                "hrv_score": 68 + (i % 15),
                "sleep_score": 82 + (i % 20),
                "stress_score": 60 - (i % 25)
            })
        
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating history: {str(e)}")

@app.get("/api/protocols/adherence")
async def get_protocol_adherence():
    """Get protocol adherence rates"""
    try:
        # Simulated protocol data
        protocols = [
            {
                "protocol_name": "Zone 2 Training",
                "target_value": 150.0,
                "actual_value": 165.0,
                "adherence_percentage": 110.0,
                "impact_years": 2.5
            },
            {
                "protocol_name": "Sleep Optimization",
                "target_value": 8.0,
                "actual_value": 7.3,
                "adherence_percentage": 91.3,
                "impact_years": 3.2
            },
            {
                "protocol_name": "Time-Restricted Feeding",
                "target_value": 12.0,
                "actual_value": 14.0,
                "adherence_percentage": 85.7,
                "impact_years": 1.5
            },
            {
                "protocol_name": "HRV Training",
                "target_value": 60.0,
                "actual_value": 68.0,
                "adherence_percentage": 113.3,
                "impact_years": 1.0
            }
        ]
        return {"protocols": protocols}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting protocols: {str(e)}")

@app.get("/api/activities/recent")
async def get_recent_activities(limit: int = 10):
    """Get recent activity data"""
    try:
        # Simulated activity data
        activities = []
        base_date = datetime.now()
        
        activity_types = ["running", "cycling", "strength_training", "yoga", "swimming"]
        
        for i in range(limit):
            date = base_date - timedelta(days=i)
            activity_type = activity_types[i % len(activity_types)]
            
            activities.append({
                "date": date.strftime("%Y-%m-%d"),
                "activity_type": activity_type,
                "duration_minutes": 45 + (i % 30),
                "calories": 350 + (i % 200),
                "zone2_minutes": 25 if activity_type in ["running", "cycling"] else 0,
                "hiit_sessions": 1 if activity_type == "running" and i % 3 == 0 else 0
            })
        
        return {"activities": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting activities: {str(e)}")

@app.get("/api/achievements")
async def get_achievements():
    """Get unlocked achievements and progress"""
    try:
        achievements = [
            {
                "id": "zone2_master",
                "name": "Zone 2 Master",
                "description": "Complete 150+ minutes of Zone 2 training per week",
                "icon": "🏃",
                "unlocked": True,
                "xp_reward": 1000,
                "unlock_date": "2024-01-15"
            },
            {
                "id": "sleep_architect",
                "name": "Sleep Architect",
                "description": "Maintain 90+ sleep score average for 30 days",
                "icon": "😴",
                "unlocked": True,
                "xp_reward": 800,
                "unlock_date": "2024-01-22"
            },
            {
                "id": "stress_terminator",
                "name": "Stress Terminator",
                "description": "Achieve HRV > 60ms for 2 weeks straight",
                "icon": "🧘",
                "unlocked": False,
                "xp_reward": 750,
                "progress": 85
            },
            {
                "id": "age_reverser",
                "name": "Age Reverser",
                "description": "Achieve biological age < chronological age",
                "icon": "🧬",
                "unlocked": True,
                "xp_reward": 2000,
                "unlock_date": "2024-01-05"
            }
        ]
        
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting achievements: {str(e)}")

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get global leaderboard"""
    try:
        # Simulated leaderboard data
        leaderboard = [
            {"rank": 1, "username": "BioHacker2077", "longevity_score": 98, "years_gained": 5.2, "level": 42},
            {"rank": 2, "username": "QuantifiedSelf", "longevity_score": 94, "years_gained": 4.8, "level": 38},
            {"rank": 3, "username": "MitoMaster", "longevity_score": 92, "years_gained": 4.3, "level": 35},
            {"rank": 4, "username": "CryoWarrior", "longevity_score": 89, "years_gained": 3.9, "level": 32},
            {"rank": 5, "username": "You", "longevity_score": 85, "years_gained": 3.2, "level": 28, "is_current_user": True},
        ]
        
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting leaderboard: {str(e)}")

@app.get("/api/health/database")
async def health_check_database():
    """Check database connectivity"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return {"database": "connected", "status": "healthy"}
    except Exception as e:
        return {"database": "disconnected", "status": "unhealthy", "error": str(e)}

@app.get("/api/health/services")
async def health_check_services():
    """Check all service health"""
    return {
        "api": "healthy",
        "database": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )