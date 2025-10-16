# 🏠 GazeHome Edge Device

Web-based gaze tracking edge device for smart home control using eye gaze. This demo runs on Raspberry Pi or similar edge devices and provides a browser-based UI for:

- **5-point gaze calibration**
- **Dwell-time based gaze clicking**
- **Smart device control via Gateway API**
- **AI-powered recommendations**
- **Real-time video feed with gaze overlay**

## 🎯 Features

### ✅ Implemented Features

1. **5-Point Calibration System**
   - Top-left, top-right, center, bottom-left, bottom-right calibration points
   - Automatic sample collection with stability filtering
   - Affine transformation for accurate gaze mapping
   - Persistent calibration storage (JSON)

2. **Gaze Tracking with Dwell-Click**
   - Integration with existing `gaze_tracking` module
   - Configurable dwell time (default 0.8s)
   - Real-time gaze pointer visualization
   - AOI (Area of Interest) mapping to devices

3. **Device Control**
   - Async HTTP client for Gateway API
   - Device list/detail/status queries
   - Device control commands
   - Periodic and manual state refresh

4. **AI Recommendations**
   - Polling-based recommendation fetching
   - YES/NO response handling
   - Automatic control execution on YES
   - Real-time popup notifications

5. **Web UI**
   - FastAPI backend with WebSocket support
   - Real-time video streaming
   - Interactive calibration interface
   - Device cards with status display
   - Recommendation popup dialogs

## 📋 Prerequisites

- Python 3.8+
- Webcam/Camera
- Gateway server running (port 8001)
- AI Service running (port 8000)

### System Requirements

```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev

# Raspberry Pi
sudo apt-get install python3-opencv
sudo apt-get install libatlas-base-dev
```

## 🚀 Quick Start

### 1. Setup

```bash
cd edge
chmod +x setup.sh
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download dlib Model

Download the facial landmarks model:

```bash
cd ../gaze_tracking/trained_models/
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### 3. Configure

Edit `config.json`:

```json
{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "ai_service_url": "http://localhost:8001",
  "mock_mode": false,
  "gaze": {
    "dwell_time": 0.8,
    "screen_width": 1920,
    "screen_height": 1080,
    "camera_index": 0
  }
}
```

### 4. Run

**Option 1: Mock Mode (UI testing without servers)**
```bash
# Set mock_mode: true in config.json
python app.py
```

**Option 2: Real Mode (with AI Service)**
```bash
# Make sure AI Service is running first!
# AI Service will communicate with Gateway

# Start edge device
python app.py
```

Open browser: **http://localhost:8000**

## 📖 Usage Guide

### First-Time Setup: Calibration

1. Click **"시선 보정 시작"** button
2. Look at each red target point for 2-3 seconds
3. The system will automatically collect samples and move to the next target
4. After all 5 points, calibration is complete and saved
5. Calibration persists across sessions in `calibration_params.json`

### Controlling Devices

**Method 1: Gaze Click (Primary)**
1. Look at a device card
2. Hold your gaze steady for ~0.8 seconds
3. A dwell indicator will grow around your gaze point
4. Click is triggered automatically
5. AI service analyzes intent and shows recommendation
6. Choose YES or NO

**Method 2: Manual Click (Fallback)**
- Click on device cards with mouse/touch

### Viewing Device Status

- Device cards show real-time status
- Green indicator = ON
- Gray indicator = OFF
- Cards update automatically every 5 seconds

### AI Recommendations

When you gaze-click a device:
1. AI analyzes your intent based on:
   - Device current state
   - Time of day
   - Weather (via MCP)
   - Historical patterns
2. Shows recommendation popup
3. Click YES to execute or NO to dismiss

## 🏗️ Architecture

```
edge/
├── app.py                 # Main FastAPI server
├── config.json           # Configuration
├── requirements.txt      # Python dependencies
├── setup.sh             # Setup script
├── test_edge.py         # Test suite
│
├── core/
│   ├── __init__.py
│   └── config.py        # Configuration manager
│
├── gaze/
│   ├── __init__.py
│   ├── calibrator.py    # 5-point calibration
│   └── tracker.py       # Gaze tracking + dwell-click
│
├── api/
│   ├── __init__.py
│   ├── gateway_client.py   # Gateway API client
│   └── ai_client.py        # AI Service API client
│
├── templates/
│   └── index.html          # Main web UI
│
└── static/
    ├── style.css          # Styles
    └── app.js             # Frontend JavaScript
```

## 🔌 API Integration

### Gateway API (Port 8001)

**Get Devices**
```http
GET /v1/devices
```

**Control Device**
```http
POST /v1/devices/{device_id}/control
Content-Type: application/json

{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "action": "toggle",
  "parameters": {}
}
```

### AI Service API (Port 8000)

**Send Device Click**
```http
POST /api/gaze/click
Content-Type: application/json

{
  "user_id": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "session_id": "session_123",
  "clicked_device": {
    "device_id": "ac_01",
    "device_type": "air_conditioner",
    "device_name": "거실 에어컨",
    "display_name": "에어컨",
    "capabilities": ["on_off", "temperature"],
    "current_state": {"is_on": false, "temperature": 24}
  }
}
```

**Poll Recommendations**
```http
GET /v1/intent?user_uuid=8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99
```

**Respond to Recommendation**
```http
POST /v1/intent
Content-Type: application/json

{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "recommendation_id": "rec_123",
  "answer": "YES"
}
```

## ⚙️ Configuration Reference

| Parameter                         | Description                               | Default                                  |
| --------------------------------- | ----------------------------------------- | ---------------------------------------- |
| `user_uuid`                       | Single user identifier for all operations | `"8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99"` |
| `ai_service_url`                  | AI service URL                            | `"http://localhost:8001"`                |
| `mock_mode`                       | Enable mock mode for UI testing           | `false`                                  |
| `gaze.dwell_time`                 | Dwell time for click (seconds)            | `0.8`                                    |
| `gaze.screen_width`               | Screen width (pixels)                     | `1920`                                   |
| `gaze.screen_height`              | Screen height (pixels)                    | `1080`                                   |
| `gaze.camera_index`               | Camera device index                       | `0`                                      |
| `polling.device_status_interval`  | Device status refresh interval (seconds)  | `5.0`                                    |
| `polling.recommendation_interval` | Recommendation poll interval (seconds)    | `3.0`                                    |

## 🧪 Testing

**Unit Tests:**
```bash
python test_edge.py
```

**Mock Mode UI Testing:**
See [MOCK_MODE_TESTING.md](./MOCK_MODE_TESTING.md) or [QUICK_START_MOCK.md](./QUICK_START_MOCK.md)

Tests include:
- Configuration loading
- Calibration system
- API client connectivity
- Gateway health check
- AI service health check

## 🐛 Troubleshooting

### Camera not detected
```bash
# List available cameras
ls /dev/video*

# Test camera
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### dlib installation fails
```bash
# macOS
brew install cmake
pip install dlib

# Ubuntu
sudo apt-get install cmake libboost-all-dev
pip install dlib
```

### Gateway/AI Service not responding
- Check servers are running: `http://localhost:8001/health`, `http://localhost:8000/health`
- Verify URLs in `config.json`
- Check firewall settings

### Calibration inaccurate
- Ensure good lighting
- Keep head still during calibration
- Recalibrate if needed (click "시선 보정 시작" again)
- Adjust `stability_threshold` in `gaze/calibrator.py`

## 📊 Performance Optimization

### For Raspberry Pi

1. **Reduce video resolution**
```python
# In app.py, before camera.read()
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

2. **Increase polling intervals**
```json
{
  "polling": {
    "device_status_interval": 10.0,
    "recommendation_interval": 5.0
  }
}
```

3. **Use hardware acceleration** (if available)
```bash
# Enable OpenCL for Raspberry Pi
sudo apt-get install ocl-icd-libopencl1
```

## 🔒 Security Considerations

⚠️ **This is a demo implementation**

For production:
- Add authentication (JWT tokens)
- Use HTTPS for API calls
- Encrypt calibration data
- Implement rate limiting
- Add CORS restrictions
- Secure WebSocket connections

## 📝 Data Flow

```
1. Camera → Gaze Tracking → Calibration Transform → Screen Coordinates
2. Screen Coordinates → Dwell Detection → Click Event
3. Click Event → AOI Mapping → Device ID + Action
4. Device Info → AI Service → Intent Analysis → Recommendation
5. Recommendation → User (YES/NO) → AI Service Response
6. YES → Gateway Control → Device State Update → UI Refresh
```

## 🎓 Future Enhancements

- [ ] WebSocket for real-time recommendations (replace polling)
- [ ] Multi-user support with face recognition
- [ ] Voice confirmation for recommendations
- [ ] Gesture-based commands (blink, nod)
- [ ] Offline mode with cached recommendations
- [ ] Progressive Web App (PWA) for mobile
- [ ] Analytics dashboard
- [ ] Custom AOI editor

## 📄 License

See main project LICENSE file.

## 🙏 Credits

- **GazeTracking**: Base gaze tracking library
- **dlib**: Facial landmark detection
- **FastAPI**: Web framework
- **OpenCV**: Computer vision

---

**Built with ❤️ for GazeHome Project**
