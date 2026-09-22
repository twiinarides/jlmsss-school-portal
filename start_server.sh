#!/bin/bash
# Startup script for Django school website

cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Check if migrations are applied
echo "Checking migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the server
echo ""
echo "========================================="
echo "Starting Django development server..."
echo "========================================="
echo "Server will be available at:"
echo "  - http://127.0.0.1:8000/"
echo "  - http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

python manage.py runserver 0.0.0.0:8000

