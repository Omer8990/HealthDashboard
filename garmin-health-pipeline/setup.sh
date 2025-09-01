#!/bin/bash

# Garmin Longevity Matrix Pipeline Setup Script
echo "🧬 Setting up Garmin Longevity Matrix Pipeline..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Garmin credentials before running the services."
    echo "   Required: GARMIN_EMAIL and GARMIN_PASSWORD"
    read -p "Press Enter when you've configured .env file..."
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p airflow/logs
mkdir -p airflow/plugins
mkdir -p data/postgres

# Set proper permissions for Airflow
echo "🔐 Setting Airflow permissions..."
echo -e "AIRFLOW_UID=$(id -u)" >> .env
sudo chown -R $(id -u):$(id -g) airflow/

# Build custom Airflow image if dockerfile exists
if [ -f docker/Dockerfile.airflow ]; then
    echo "🐳 Building custom Airflow image..."
    docker build -t garmin-airflow:latest -f docker/Dockerfile.airflow docker/
fi

# Start PostgreSQL first
echo "🐘 Starting PostgreSQL..."
docker-compose up -d postgres
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize Airflow database
echo "🌬️ Initializing Airflow..."
docker-compose up airflow-init

# Start all core services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Display service URLs
echo ""
echo "✅ Setup complete! Services are starting up..."
echo ""
echo "🌐 Access Points:"
echo "   📊 Airflow UI:        http://localhost:8080 (admin/admin)"
echo "   🚀 Spark Master UI:   http://localhost:8081"
echo "   🐘 PostgreSQL:        localhost:5432 (postgres/postgres)"
echo "   🌺 Flower (optional): docker-compose --profile flower up -d"
echo "   📱 Dashboard:         docker-compose --profile dashboard up -d"
echo ""
echo "⏳ Services may take a few minutes to fully initialize."
echo "💡 Check service status: docker-compose ps"
echo "📋 View logs: docker-compose logs [service-name]"
echo ""
echo "🧬 Ready to hack your longevity! 🚀"