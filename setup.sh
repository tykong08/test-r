#!/bin/bash

# GazeHome Edge Device - Quick Start Script

echo "🏠 GazeHome Edge Device Setup"
echo "=============================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download dlib model if not exists
MODEL_PATH="../gaze_tracking/trained_models/shape_predictor_68_face_landmarks.dat"
if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️  Warning: dlib model not found at $MODEL_PATH"
    echo "Please download shape_predictor_68_face_landmarks.dat"
    echo "from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the edge device:"
echo "  python app.py"
echo ""
echo "Then open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "Make sure Gateway and AI Service are running:"
echo "  Gateway:     http://localhost:8001"
echo "  AI Service:  http://localhost:8000"
echo ""
