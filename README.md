# GazeHome Edge Device# 🏠 GazeHome Edge Device



시선 추적 기반 스마트홈 제어 시스템의 Edge Device 구현체입니다. 신체적 장애가 있는 사용자를 위한 접근성 솔루션으로, 시선과 깜빡임만으로 스마트홈 디바이스를 제어할 수 있습니다.Web-based gaze tracking edge device for smart home control using eye gaze. This demo runs on Raspberry Pi or similar edge devices and provides a browser-based UI for:



## 🎯 주요 기능- **5-point gaze calibration**

- **Dwell-time based gaze clicking**

- **시선 추적 (Gaze Tracking)**: dlib 기반 실시간 시선 위치 추적- **Smart device control via Gateway API**

- **이중 클릭 모드**: - **AI-powered recommendations**

  - Dwell Click: 일정 시간 응시로 클릭- **Real-time video feed with gaze overlay**

  - Blink Click: 의도적인 깜빡임으로 클릭

- **시선 보정 (Calibration)**: 5포인트 보정으로 정확도 향상## 🎯 Features

- **실시간 웹 UI**: WebSocket 기반 실시간 시선 포인터 표시

- **AI 추천 시스템**: AI 서비스와 연동한 스마트 제어 추천### ✅ Implemented Features



## 📁 프로젝트 구조1. **5-Point Calibration System**

   - Top-left, top-right, center, bottom-left, bottom-right calibration points

```   - Automatic sample collection with stability filtering

edge/   - Affine transformation for accurate gaze mapping

├── app.py                      # FastAPI 메인 애플리케이션   - Persistent calibration storage (JSON)

├── config.json                 # 설정 파일

├── requirements.txt            # Python 의존성2. **Gaze Tracking with Dwell-Click**

├── core/                       # 핵심 모듈   - Integration with existing `gaze_tracking` module

│   ├── config.py              # 설정 관리   - Configurable dwell time (default 0.8s)

│   └── database.py            # 데이터베이스 (SQLite)   - Real-time gaze pointer visualization

├── gaze/                       # 시선 추적 모듈   - AOI (Area of Interest) mapping to devices

│   ├── tracker.py             # GazeTracker (메인)

│   └── calibrator.py          # 시선 보정3. **Device Control**

├── model/                      # ML 모델 (이전 gaze_tracking)   - Async HTTP client for Gateway API

│   ├── gaze_tracking.py       # 시선 추적 라이브러리   - Device list/detail/status queries

│   ├── eye.py                 # 눈 감지   - Device control commands

│   ├── pupil.py               # 동공 감지   - Periodic and manual state refresh

│   └── calibration.py         # 보정 알고리즘

├── services/                   # 외부 서비스 연동4. **AI Recommendations**

│   ├── ai_service.py          # AI 서비스 클라이언트   - Polling-based recommendation fetching

│   └── device_manager.py      # 디바이스 관리   - YES/NO response handling

├── templates/                  # HTML 템플릿   - Automatic control execution on YES

│   └── index.html             # 메인 UI   - Real-time popup notifications

└── static/                     # 정적 파일

    ├── app.js                 # 프론트엔드 로직5. **Web UI**

    └── style.css              # 스타일시트   - FastAPI backend with WebSocket support

```   - Real-time video streaming

   - Interactive calibration interface

## 🚀 빠른 시작   - Device cards with status display

   - Recommendation popup dialogs

### 1. 환경 설정

## 📋 Prerequisites

```bash

# Conda 환경 생성 및 활성화- Python 3.8+

conda create -n gaze python=3.11- Webcam/Camera

conda activate gaze- Gateway server running (port 8001)

- AI Service running (port 8000)

# 의존성 설치

cd edge### System Requirements

pip install -r requirements.txt

``````bash

# macOS

### 2. 설정 파일 수정brew install cmake



`config.json`:# Ubuntu/Debian

```jsonsudo apt-get install build-essential cmake

{sudo apt-get install libopenblas-dev liblapack-dev

    "user_uuid": "your-uuid-here",sudo apt-get install libx11-dev libgtk-3-dev

    "ai_service_url": "http://localhost:8001",

    "mock_mode": true,  // 테스트용: true, 프로덕션: false# Raspberry Pi

    "gaze": {sudo apt-get install python3-opencv

        "dwell_time": 0.8,sudo apt-get install libatlas-base-dev

        "screen_width": 1920,```

        "screen_height": 1080,

        "camera_index": 0## 🚀 Quick Start

    }

}### 1. Setup

```

```bash

### 3. 서버 실행cd edge

chmod +x setup.sh

```bash./setup.sh

python app.py```

```

Or manually:

브라우저에서 `http://localhost:8000` 접속

```bash

## 🎮 사용 방법# Create virtual environment

python3 -m venv venv

### 시선 보정source venv/bin/activate  # On Windows: venv\Scripts\activate



1. "시선 보정 시작" 버튼 클릭# Install dependencies

2. 화면에 나타나는 빨간 점을 응시pip install -r requirements.txt

3. 5개 포인트 × 30샘플 수집```

4. 보정 완료 후 자동으로 저장

### 2. Download dlib Model

**보정 팁:**

- 얼굴을 화면 중앙에 위치Download the facial landmarks model:

- 충분한 조명 확보 (정면 조명 권장)

- 카메라와 40-60cm 거리 유지```bash

cd ../gaze_tracking/trained_models/

### 클릭 모드wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

bunzip2 shape_predictor_68_face_landmarks.dat.bz2

#### Dwell Click (응시 클릭)```

- 대상을 0.8초 이상 응시

- 진행 상황이 파란 원으로 표시### 3. Configure

- 시간 완료 시 자동 클릭

Edit `config.json`:

#### Blink Click (깜빡임 클릭)

- 0.3~1.0초 사이의 의도적 깜빡임```json

- 자연스러운 깜빡임은 무시 (< 0.3초){

  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",

**민감도 조정:**  "ai_service_url": "http://localhost:8001",

보정 화면에서 "응시 민감도" 슬라이더로 조정 가능 (0.3~2.0초)  "mock_mode": false,

  "gaze": {

## 🔌 API 문서    "dwell_time": 0.8,

    "screen_width": 1920,

### REST API    "screen_height": 1080,

    "camera_index": 0

#### 1. 상태 조회  }

```http}

GET /api/state```

```

### 4. Run

**Response:**

```json**Option 1: Mock Mode (UI testing without servers)**

{```bash

  "user_uuid": "8f6b3c54-...",# Set mock_mode: true in config.json

  "calibrated": true,python app.py

  "devices": [```

    {

      "device_id": "ac_living_room",**Option 2: Real Mode (with AI Service)**

      "name": "거실 에어컨",```bash

      "device_type": "air_conditioner",# Make sure AI Service is running first!

      "current_state": {# AI Service will communicate with Gateway

        "is_on": true,

        "temperature": 24# Start edge device

      }python app.py

    }```

  ],

  "recommendation": nullOpen browser: **http://localhost:8000**

}

```## 📖 Usage Guide



#### 2. 디바이스 제어### First-Time Setup: Calibration

```http

POST /api/devices/{device_id}/control1. Click **"시선 보정 시작"** button

Content-Type: application/json2. Look at each red target point for 2-3 seconds

3. The system will automatically collect samples and move to the next target

{4. After all 5 points, calibration is complete and saved

  "action": "toggle",  // or "turn_on", "turn_off", "set_temperature"5. Calibration persists across sessions in `calibration_params.json`

  "parameters": {      // 선택적

    "temperature": 24### Controlling Devices

  }

}**Method 1: Gaze Click (Primary)**

```1. Look at a device card

2. Hold your gaze steady for ~0.8 seconds

#### 3. 시선 보정3. A dwell indicator will grow around your gaze point

4. Click is triggered automatically

**보정 시작:**5. AI service analyzes intent and shows recommendation

```http6. Choose YES or NO

POST /api/calibration/start

```**Method 2: Manual Click (Fallback)**

- Click on device cards with mouse/touch

**샘플 추가:**

```http### Viewing Device Status

POST /api/calibration/sample

```- Device cards show real-time status

- Green indicator = ON

**다음 타겟으로 이동:**- Gray indicator = OFF

```http- Cards update automatically every 5 seconds

POST /api/calibration/next

```### AI Recommendations



**진행 상황 조회:**When you gaze-click a device:

```http1. AI analyzes your intent based on:

GET /api/calibration/progress   - Device current state

```   - Time of day

   - Weather (via MCP)

**Response:**   - Historical patterns

```json2. Shows recommendation popup

{3. Click YES to execute or NO to dismiss

  "is_complete": false,

  "current_target": 0,## 🏗️ Architecture

  "total_targets": 5,

  "current_samples": 15,```

  "required_samples": 30,edge/

  "target_position": [960, 540]├── app.py                 # Main FastAPI server

}├── config.json           # Configuration

```├── requirements.txt      # Python dependencies

├── setup.sh             # Setup script

#### 4. 응시 시간 설정├── test_edge.py         # Test suite

```http│

POST /api/dwell-time├── core/

Content-Type: application/json│   ├── __init__.py

│   └── config.py        # Configuration manager

{│

  "dwell_time": 0.8├── gaze/

}│   ├── __init__.py

```│   ├── calibrator.py    # 5-point calibration

│   └── tracker.py       # Gaze tracking + dwell-click

### WebSocket API│

├── api/

```javascript│   ├── __init__.py

const ws = new WebSocket('ws://localhost:8000/ws');│   ├── gateway_client.py   # Gateway API client

│   └── ai_client.py        # AI Service API client

ws.onmessage = (event) => {│

  const data = JSON.parse(event.data);├── templates/

  │   └── index.html          # Main web UI

  switch(data.type) {│

    case 'gaze':└── static/

      // 시선 위치 업데이트    ├── style.css          # Styles

      console.log(data.position); // {x: 960, y: 540}    └── app.js             # Frontend JavaScript

      break;```

      

    case 'click':## 🔌 API Integration

      // 클릭 이벤트

      console.log(data.device_id);### Gateway API (Port 8001)

      console.log(data.method); // 'dwell' or 'blink'

      break;**Get Devices**

      ```http

    case 'dwell':GET /v1/devices

      // Dwell 진행도```

      console.log(data.progress); // 0.0 ~ 1.0

      break;**Control Device**

      ```http

    case 'state':POST /v1/devices/{device_id}/control

      // 시스템 상태 업데이트Content-Type: application/json

      console.log(data.devices);

      break;{

  }  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",

};  "action": "toggle",

```  "parameters": {}

}

## 🤖 AI 서비스 연동```



### AI Service API### AI Service API (Port 8000)



Edge Device는 별도의 AI Service와 통신합니다:**Send Device Click**

```http

**추천 요청:**POST /api/gaze/click

```httpContent-Type: application/json

POST http://localhost:8001/api/recommendations

Content-Type: application/json{

  "user_id": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",

{  "session_id": "session_123",

  "user_uuid": "8f6b3c54-...",  "clicked_device": {

  "context": {    "device_id": "ac_01",

    "time": "2024-01-01T14:30:00",    "device_type": "air_conditioner",

    "devices": [...]    "device_name": "거실 에어컨",

  }    "display_name": "에어컨",

}    "capabilities": ["on_off", "temperature"],

```    "current_state": {"is_on": false, "temperature": 24}

  }

**디바이스 제어 전송:**}

```http```

POST http://localhost:8001/api/device-control

Content-Type: application/json**Poll Recommendations**

```http

{GET /v1/intent?user_uuid=8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99

  "user_uuid": "8f6b3c54-...",```

  "device_id": "ac_living_room",

  "action": "turn_on",**Respond to Recommendation**

  "method": "gaze_blink"```http

}POST /v1/intent

```Content-Type: application/json



## 🌉 Gateway 연동{

  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",

Gateway와의 통신은 AI Service를 통해 이루어집니다:  "recommendation_id": "rec_123",

  "answer": "YES"

```}

Edge Device -> AI Service -> Gateway -> Smart Device```

```

## ⚙️ Configuration Reference

**Mock 모드:**

- `mock_mode: true`: 가상 디바이스로 테스트| Parameter                         | Description                               | Default                                  |

- `mock_mode: false`: 실제 Gateway 연동| --------------------------------- | ----------------------------------------- | ---------------------------------------- |

| `user_uuid`                       | Single user identifier for all operations | `"8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99"` |

## 🖥️ UI 구성| `ai_service_url`                  | AI service URL                            | `"http://localhost:8001"`                |

| `mock_mode`                       | Enable mock mode for UI testing           | `false`                                  |

### 메인 화면| `gaze.dwell_time`                 | Dwell time for click (seconds)            | `0.8`                                    |

| `gaze.screen_width`               | Screen width (pixels)                     | `1920`                                   |

- **헤더**: 보정 상태, 연결 상태| `gaze.screen_height`              | Screen height (pixels)                    | `1080`                                   |

- **시선 포인터**: 전체 화면에 녹색 포인터 표시| `gaze.camera_index`               | Camera device index                       | `0`                                      |

- **Dwell 진행도**: 응시 중인 대상에 파란 원 표시| `polling.device_status_interval`  | Device status refresh interval (seconds)  | `5.0`                                    |

- **제어 패널**: 보정 시작, 기기 새로고침| `polling.recommendation_interval` | Recommendation poll interval (seconds)    | `3.0`                                    |

- **디바이스 그리드**: 연결된 스마트 디바이스 카드

## 🧪 Testing

### 보정 화면

**Unit Tests:**

- **타겟 포인트**: 빨간 점 (5개 위치)```bash

- **웹캠 프리뷰**: 우측 하단에 얼굴 확인용python test_edge.py

- **진행 바**: 현재 포인트 및 샘플 수```

- **민감도 조정**: 응시 시간 슬라이더

**Mock Mode UI Testing:**

## 🔧 문제 해결See [MOCK_MODE_TESTING.md](./MOCK_MODE_TESTING.md) or [QUICK_START_MOCK.md](./QUICK_START_MOCK.md)



### 카메라가 열리지 않음Tests include:

```bash- Configuration loading

# 카메라 인덱스 확인- Calibration system

python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"- API client connectivity

- Gateway health check

# config.json에서 camera_index 수정- AI service health check

```

## 🐛 Troubleshooting

### 동공 감지 안 됨 (pupils_detected=False)

- 조명을 밝게 조정### Camera not detected

- 얼굴을 화면 정면에 위치```bash

- 카메라와의 거리 조정 (40-60cm)# List available cameras

- 안경이 빛을 반사하는 경우 각도 조정ls /dev/video*



### WebSocket 연결 끊김# Test camera

```bashpython -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# uvicorn[standard] 재설치```

pip install --upgrade 'uvicorn[standard]'

```### dlib installation fails

```bash

### import 오류# macOS

```bashbrew install cmake

# 경로 확인pip install dlib

echo $PYTHONPATH

# Ubuntu

# 환경 재설정sudo apt-get install cmake libboost-all-dev

cd edgepip install dlib

export PYTHONPATH="${PYTHONPATH}:$(pwd)"```

python app.py

```### Gateway/AI Service not responding

- Check servers are running: `http://localhost:8001/health`, `http://localhost:8000/health`

## 📊 성능 최적화- Verify URLs in `config.json`

- Check firewall settings

### 프레임 레이트

- 권장: 30 FPS### Calibration inaccurate

- config에서 조정 가능- Ensure good lighting

- 낮은 사양에서는 15 FPS로 감소- Keep head still during calibration

- Recalibrate if needed (click "시선 보정 시작" again)

### 메모리 사용량- Adjust `stability_threshold` in `gaze/calibrator.py`

- 기본: ~500MB

- dlib 모델 로딩: ~100MB## 📊 Performance Optimization

- 웹캠 버퍼: ~50MB

### For Raspberry Pi

## 🔒 보안

1. **Reduce video resolution**

- HTTPS 지원 (프로덕션 환경)```python

- UUID 기반 사용자 인증# In app.py, before camera.read()

- AI Service와 토큰 기반 통신camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

## 📝 로그```



로그 레벨 설정:2. **Increase polling intervals**

```python```json

# app.py{

logging.basicConfig(level=logging.INFO)  # DEBUG, INFO, WARNING, ERROR  "polling": {

```    "device_status_interval": 10.0,

    "recommendation_interval": 5.0

주요 로그:  }

- `Camera Status: OPEN` - 카메라 정상 작동}

- `Gaze result: position=(x, y), pupils_detected=True` - 시선 추적 성공```

- `Blink click detected: 0.45s` - 깜빡임 클릭 감지

- `Click detected (dwell): device_id at (x, y)` - 응시 클릭 감지3. **Use hardware acceleration** (if available)

```bash

## 🧪 테스트# Enable OpenCL for Raspberry Pi

sudo apt-get install ocl-icd-libopencl1

### 브랜치별 모드```



- **main**: 프로덕션 모드 (`mock_mode: false`)## 🔒 Security Considerations

- **test**: 개발/테스트 모드 (`mock_mode: true`)

⚠️ **This is a demo implementation**

```bash

# 테스트 브랜치로 전환For production:

git checkout test- Add authentication (JWT tokens)

- Use HTTPS for API calls

# 프로덕션 브랜치로 전환- Encrypt calibration data

git checkout main- Implement rate limiting

```- Add CORS restrictions

- Secure WebSocket connections

## 🤝 기여

## 📝 Data Flow

이슈 및 Pull Request 환영합니다!

```

## 📄 라이선스1. Camera → Gaze Tracking → Calibration Transform → Screen Coordinates

2. Screen Coordinates → Dwell Detection → Click Event

이 프로젝트는 접근성 향상을 목표로 개발되었습니다.3. Click Event → AOI Mapping → Device ID + Action

4. Device Info → AI Service → Intent Analysis → Recommendation

## 📞 문의5. Recommendation → User (YES/NO) → AI Service Response

6. YES → Gateway Control → Device State Update → UI Refresh

문제가 발생하면 GitHub Issues에 등록해주세요.```



---## 🎓 Future Enhancements



**개발 환경:**- [ ] WebSocket for real-time recommendations (replace polling)

- Python 3.11- [ ] Multi-user support with face recognition

- FastAPI 0.104- [ ] Voice confirmation for recommendations

- OpenCV 4.8- [ ] Gesture-based commands (blink, nod)

- dlib 19.24- [ ] Offline mode with cached recommendations

- WebSocket (uvicorn[standard])- [ ] Progressive Web App (PWA) for mobile

- [ ] Analytics dashboard

**테스트 환경:**- [ ] Custom AOI editor

- macOS / Raspberry Pi OS

- 웹캠: 내장 카메라 or USB 카메라## 📄 License

- 브라우저: Chrome, Firefox, Safari (최신 버전)

See main project LICENSE file.

## 🙏 Credits

- **GazeTracking**: Base gaze tracking library
- **dlib**: Facial landmark detection
- **FastAPI**: Web framework
- **OpenCV**: Computer vision

---

**Built with ❤️ for GazeHome Project**
