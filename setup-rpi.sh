#!/bin/bash

# GazeHome Edge Device - Raspberry Pi Quick Setup Script
# This script automates the installation process on Raspberry Pi

set -e  # Exit on error

echo "================================================"
echo "  GazeHome Edge Device - Raspberry Pi Setup"
echo "================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${RED}Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

echo ""
echo -e "${GREEN}Step 2: Installing system dependencies...${NC}"
sudo apt install -y \
    build-essential \
    cmake \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libboost-all-dev \
    libv4l-dev \
    v4l-utils \
    python3-pip \
    python3-venv

echo ""
echo -e "${GREEN}Step 3: Creating Python virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
fi

source venv/bin/activate

echo ""
echo -e "${GREEN}Step 4: Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

echo ""
echo -e "${YELLOW}Step 5: Installing Python packages (this may take a while)...${NC}"
pip install -r requirements-rpi.txt

echo ""
echo -e "${YELLOW}Step 6: Installing dlib (this will take 1-2 hours)...${NC}"
read -p "Do you want to build dlib from source? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Try piwheels first (much faster)
    echo "Trying piwheels first..."
    pip install dlib --extra-index-url https://www.piwheels.org/simple || {
        echo "piwheels failed, building from source..."
        
        # Increase swap for compilation
        echo "Increasing swap memory..."
        sudo dphys-swapfile swapoff
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
        sudo dphys-swapfile setup
        sudo dphys-swapfile swapon
        
        # Install dlib
        pip install dlib
        
        # Restore swap
        echo "Restoring swap memory..."
        sudo dphys-swapfile swapoff
        sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=100/' /etc/dphys-swapfile
        sudo dphys-swapfile setup
        sudo dphys-swapfile swapon
    }
else
    echo "Skipping dlib installation. You can install it later."
fi

echo ""
echo -e "${GREEN}Step 7: Checking camera...${NC}"
if ls /dev/video* 1> /dev/null 2>&1; then
    echo -e "${GREEN}Camera found:${NC}"
    ls -l /dev/video*
    
    # Add user to video group
    sudo usermod -a -G video $USER
    echo "Added user to 'video' group. Please log out and log back in for this to take effect."
else
    echo -e "${RED}No camera detected. Please connect a camera.${NC}"
fi

echo ""
echo -e "${GREEN}Step 8: Creating configuration file...${NC}"
if [ -f "config.json" ]; then
    echo "config.json already exists. Skipping..."
else
    cat > config.json <<EOF
{
    "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
    "ai_service_url": "http://localhost:8001",
    "mock_mode": true,
    "gaze": {
        "dwell_time": 0.8,
        "calibration_points": 5,
        "screen_width": 1280,
        "screen_height": 720,
        "camera_index": 0
    },
    "polling": {
        "device_status_interval": 5.0,
        "recommendation_interval": 3.0
    },
    "calibration_file": "calibration_params.json"
}
EOF
    echo "Created config.json with default settings (Mock Mode enabled)"
fi

echo ""
echo -e "${GREEN}Step 9: Testing installation...${NC}"
python -c "
import cv2
import numpy
import fastapi
import uvicorn
print('✅ All core packages imported successfully!')
"

echo ""
echo "================================================"
echo -e "${GREEN}  Installation Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit config.json to set your AI Service URL"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the server: python app.py"
echo "4. Access from browser: http://<raspberry-pi-ip>:8000"
echo ""
echo "For more details, see RASPBERRY_PI_SETUP.md"
echo ""

read -p "Do you want to create a systemd service for auto-start? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    VENV_PYTHON="$CURRENT_DIR/venv/bin/python"
    
    sudo tee /etc/systemd/system/gazehome-edge.service > /dev/null <<EOF
[Unit]
Description=GazeHome Edge Device
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$VENV_PYTHON $CURRENT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable gazehome-edge.service
    
    echo -e "${GREEN}Systemd service created and enabled!${NC}"
    echo "Start service: sudo systemctl start gazehome-edge.service"
    echo "Check status: sudo systemctl status gazehome-edge.service"
fi

echo ""
echo -e "${GREEN}Setup complete! 🍓✨${NC}"
