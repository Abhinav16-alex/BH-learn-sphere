# BH LearnSphere - AI-Powered Adaptive Learning Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

BH LearnSphere is a next-generation Learning Management System (LMS) featuring AI-powered adaptive learning, real-time collaboration, and comprehensive course management.

## ✨ Features

- **Role-Based Authentication** - Admin, Instructor, Student roles with JWT
- **Course Management** - Create, update, publish courses with modules and lessons
- **Multiple Content Types** - Video, PDF, Text, Quizzes, Assignments
- **AI Recommendations** - Personalized course suggestions using ML
- **Adaptive Learning Paths** - Adjusts based on student performance
- **Real-Time Chat** - WebSocket-based chat rooms for courses
- **Discussion Forums** - Course-specific forums and threads
- **Assessments** - Auto-graded quizzes with multiple question types
- **Analytics Dashboard** - Track progress, engagement, and performance
- **Payment Integration** - Stripe integration with coupons
- **Gamification** - Badges and points system

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/bh-learnsphere.git
cd bh-learnsphere

# Run setup script
chmod +x setup.sh
./setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Create database
createdb learnsphere_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
