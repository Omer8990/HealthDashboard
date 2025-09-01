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

## 🎯 Mission Statement

The **Longevity Matrix** is designed with a singular goal: **to optimize your biological age and maximize healthspan through data-driven anti-aging protocols**. By transforming health tracking into an engaging cyberpunk RPG experience, we make longevity optimization addictive, motivating you to consistently implement evidence-based interventions that slow or reverse biological aging.

This isn't just another fitness dashboard – it's your personal anti-aging command center, designed to help you:
- 🧬 **Reverse your biological age** through targeted protocols
- 📊 **Track hallmarks of aging** with scientific precision
- 🎮 **Gamify longevity** with achievements, levels, and leaderboards
- 🚀 **Reach escape velocity** – add more than one year of life per year lived
- 💊 **Optimize interventions** based on real biomarker feedback

## ✨ Key Features

### 🔬 Longevity-Focused Analytics
- **Biological Age Calculation**: Advanced algorithms analyze VO2 max, HRV, sleep quality, and body composition
- **Aging Velocity Tracking**: Monitor if you're aging slower than chronological time
- **Hallmarks of Aging Dashboard**: Track 9 scientific markers of biological aging
- **Protocol Effectiveness**: Measure the impact of each intervention in "years gained"
- **Biomarker Optimization**: Real-time feedback on key longevity markers

### 🎮 Gamification System
- **RPG Progression**: Level up from "Biohacker Initiate" to "Immortality Architect"
- **XP & Achievements**: Earn experience for maintaining longevity protocols
- **Global Leaderboard**: Compete with other longevity enthusiasts worldwide
- **Streak Tracking**: Build consistency with visual streak counters
- **Protocol Challenges**: Weekly and monthly longevity challenges

### 📈 Anti-Aging Protocols Tracked
- **Zone 2 Training**: Mitochondrial optimization (150+ min/week)
- **HIIT Sessions**: VO2 max improvement
- **Time-Restricted Feeding**: Autophagy activation
- **Sleep Optimization**: 7-9 hours with proper sleep architecture
- **Cold Exposure**: Hormetic stress adaptation
- **Heat Therapy**: Sauna sessions for cardiovascular health
- **Strength Training**: Sarcopenia prevention
- **Meditation/HRV Training**: Stress resilience

### 🎨 Cyberpunk Aesthetic
- **Neon Color Scheme**: Cyan, magenta, and purple glowing interfaces
- **Animated Visualizations**: Real-time data with particle effects
- **Matrix-Style Overlays**: Grid patterns and scan lines
- **Holographic Elements**: 3D-effect cards and displays
- **Achievement Badges**: Unlock futuristic badges for milestones

## 🏗️ Architecture

```mermaid
graph TB
    A[Garmin Connect] -->|API| B[Data Extraction Layer]
    B --> C[PostgreSQL Staging]
    C --> D[Apache Spark Processing]
    D --> E[Processed Data Store]
    E --> F[Apache Airflow Orchestration]
    F --> G[Materialized Views]
    G --> H[REST API]
    H --> I[Cyberpunk Dashboard]
    
    style A fill:#00ffff
    style I fill:#ff00ff
    style D fill:#ffff00
```

### Components

1. **Data Extraction** (`extraction/`)
   - Connects to Garmin Connect API
   - Extracts comprehensive health metrics
   - Handles authentication and rate limiting

2. **Data Processing** (`spark/`)
   - PySpark jobs for complex calculations
   - Biological age algorithms
   - Protocol adherence scoring
   - Personal record detection

3. **Orchestration** (`airflow/`)
   - Daily automated syncs
   - Historical data backfilling
   - Data quality monitoring
   - Weekly/monthly aggregations

4. **Database** (`database/`)
   - Staging tables for raw data
   - Processed metrics storage
   - Longevity-specific calculations
   - Performance-optimized views

5. **Dashboard** (`dashboard/`)
   - React/Next.js frontend
   - Real-time WebSocket updates
   - Interactive D3.js visualizations
   - Gamification engine

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 13+
- Apache Spark 3.0+
- Node.js 16+
- Garmin Connect account

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/garmin-longevity-matrix.git
cd garmin-longevity-matrix
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```env
GARMIN_EMAIL=your_garmin_email
GARMIN_PASSWORD=your_garmin_password
DATABASE_URL=postgresql://user:pass@localhost:5432/longevity
AIRFLOW_HOME=/path/to/airflow
SPARK_HOME=/path/to/spark
```

3. **Initialize the database**
```bash
psql -U postgres -c "CREATE DATABASE longevity;"
psql -U postgres -d longevity -f database/init.sql
```

4. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

5. **Start services with Docker Compose**
```bash
docker-compose up -d
```

6. **Initialize Airflow**
```bash
airflow db init
airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
airflow webserver -D
airflow scheduler -D
```

7. **Install and start the dashboard**
```bash
cd dashboard
npm install
npm run dev
```

8. **Access the applications**
- Dashboard: http://localhost:3000
- Airflow: http://localhost:8080
- PostgreSQL: localhost:5432

## 📊 Data Pipeline

### Daily Sync Workflow
1. **6:00 AM**: Automated Garmin data extraction
2. **6:15 AM**: Spark processing jobs
3. **6:30 AM**: Biological age calculation
4. **6:45 AM**: Protocol scoring updates
5. **7:00 AM**: Dashboard refresh with new metrics

### Longevity Metrics Calculated
- **Biological Age**: Multi-factor algorithm based on:
  - VO2 Max (weight: 30%)
  - HRV Score (weight: 20%)
  - Sleep Quality (weight: 20%)
  - Body Composition (weight: 15%)
  - Stress Levels (weight: 15%)

- **Aging Velocity**: Rate of biological aging vs chronological time
- **Protocol Impact**: Years gained/lost per intervention
- **Longevity Score**: 0-100 composite score across 6 domains

## 🎮 Gamification Features

### Achievement System
| Achievement | Requirement | XP Reward |
|------------|-------------|-----------|
| 🏃 **Zone 2 Master** | 150+ min/week for 4 weeks | 1000 XP |
| 😴 **Sleep Architect** | 90+ sleep score average for 30 days | 800 XP |
| 🧘 **Stress Terminator** | HRV > 60ms for 2 weeks | 750 XP |
| 🥶 **Cryogenic Warrior** | Cold exposure 20x/month | 900 XP |
| 🔥 **Heat Shock Hero** | Sauna 12x/month | 850 XP |
| 💪 **Sarcopenia Slayer** | 3x strength/week for 8 weeks | 950 XP |
| 🧬 **Age Reverser** | Bio age < chrono age | 2000 XP |
| 🚀 **Escape Velocity** | -1 year bio age in 6 months | 5000 XP |

### Level Progression
- **Level 1-10**: Biohacker Initiate
- **Level 11-25**: Longevity Apprentice
- **Level 26-40**: Age Hacker
- **Level 41-60**: Longevity Master
- **Level 61-80**: Immortality Seeker
- **Level 81-99**: Singularity Architect
- **Level 100**: Transcendent

## 🔬 Scientific Basis

The dashboard tracks interventions based on peer-reviewed longevity research:

- **Peter Attia's Framework**: Zone 2, VO2 max, strength training
- **David Sinclair's Protocols**: NAD+ optimization, hormesis
- **Valter Longo's Research**: Time-restricted feeding, fasting
- **Matt Walker's Sleep Science**: Sleep architecture optimization
- **Rhonda Patrick's Insights**: Heat/cold therapy, micronutrients
- **Bryan Johnson's Blueprint**: Comprehensive biomarker tracking

## 📱 Dashboard Views

### 1. **Command Center**
- Biological vs chronological age display
- Aging velocity chart
- Real-time protocol adherence
- Today's optimization score

### 2. **Protocols**
- Active intervention tracking
- Adherence percentages
- Impact in years gained
- Recommended new protocols

### 3. **Biomarkers**
- VO2 Max trends
- HRV analysis
- Body composition
- Inflammation markers
- Sleep architecture

### 4. **Achievements**
- Unlocked badges
- Progress toward next achievement
- Global leaderboard position
- Monthly challenges

## 🛠️ Configuration

### Customize Biological Age Algorithm
Edit `spark/jobs/longevity_calculator.py`:
```python
AGING_WEIGHTS = {
    'vo2_max': 0.30,
    'hrv': 0.20,
    'sleep': 0.20,
    'body_composition': 0.15,
    'stress': 0.15
}
```

### Add Custom Protocols
Edit `database/protocols.sql`:
```sql
INSERT INTO longevity_protocols (name, category, impact_years, difficulty)
VALUES ('Your Protocol', 'category', 1.5, 'Medium');
```

## 📈 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/biological-age` | GET | Current biological age calculation |
| `/api/protocols` | GET | Active protocols and adherence |
| `/api/achievements` | GET | Unlocked achievements |
| `/api/biomarkers` | GET | Latest biomarker values |
| `/api/leaderboard` | GET | Global rankings |
| `/api/aging-velocity` | GET | Aging rate over time |

## 🤝 Contributing

We welcome contributions to help more people optimize their longevity! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority Areas
- Additional biomarker integrations (CGM, wearables)
- More sophisticated aging algorithms
- Social features and challenges
- Mobile app development
- ML-based protocol recommendations

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Garmin** for comprehensive health data access
- **Apache** for Spark and Airflow
- **Anthropic** for AI assistance
- **Longevity researchers** for the scientific foundation
- **r/longevity** and **r/Biohackers** communities

## ⚠️ Disclaimer

This dashboard is for informational purposes only and should not replace professional medical advice. Always consult with healthcare providers before making significant changes to your health protocols. The biological age calculations are estimates based on available data and may not reflect your actual biological age.

## 🚀 Future Roadmap

- [ ] Integration with additional wearables (Whoop, Oura, Apple Watch)
- [ ] Blood biomarker tracking integration
- [ ] AI-powered protocol recommendations
- [ ] Social challenges and team competitions
- [ ] Genetic data integration (23andMe, etc.)
- [ ] Supplement stack optimization
- [ ] Virtual longevity coach
- [ ] Blockchain-based achievement NFTs
- [ ] VR meditation integration
- [ ] Longevity cryptocurrency rewards

---

<p align="center">
  <strong>🧬 Hack your biology. Reverse your age. Reach the future. 🚀</strong>
</p>

<p align="center">
  Built with 💜 for the longevity community
</p>