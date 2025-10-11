#!/bin/bash
# Save as: setup.sh

echo "======================================"
echo "BH LearnSphere - Setup Script"
echo "======================================"

# Check Python version
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ".env file created. Please update it with your credentials!"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p media/profiles
mkdir -p media/badges
mkdir -p media/course_thumbnails
mkdir -p media/lesson_videos
mkdir -p media/lesson_pdfs
mkdir -p media/assignment_submissions
mkdir -p static
mkdir -p staticfiles
mkdir -p templates

# Database setup reminder
echo ""
echo "======================================"
echo "Next Steps:"
echo "======================================"
echo "1. Update .env file with your database credentials"
echo "2. Create PostgreSQL database:"
echo "   createdb learnsphere_db"
echo "3. Run migrations:"
echo "   python manage.py makemigrations"
echo "   python manage.py migrate"
echo "4. Create superuser:"
echo "   python manage.py createsuperuser"
echo "5. Run server:"
echo "   python manage.py runserver"
echo "======================================"

# Make script executable: chmod +x setup.sh
