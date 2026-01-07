#!/bin/bash
# DarkNetwork Quick Start Script

set -e  # Exit on any error

echo "🚀 Starting DarkNetwork Setup..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate

# Create superuser (if needed)
echo ""
read -p "Do you want to create a superuser? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run health check
echo ""
echo "🏥 Running health check..."
python check_health.py

# Start server
echo ""
echo "✅ Setup complete!"
echo ""
read -p "Do you want to start the development server? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🌐 Starting server at http://127.0.0.1:8000/"
    echo "   Press Ctrl+C to stop"
    echo ""
    python manage.py runserver
fi
