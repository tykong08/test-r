# GazeHome Edge Device# 🏠 GazeHome Edge Device# 🏠 GazeHome Edge Device



[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)](https://opencv.org/)[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)

시선 추적 기반 스마트홈 제어 시스템

[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)](https://opencv.org/)[![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-red.svg)](https://opencv.org/)

---

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 기능



- **시선 추적**: dlib 기반 68-point facial landmark 감지

- **5-Point 보정**: 화면 5개 포인트 보정 (Affine 변환)> **시선 추적 기반 스마트홈 제어 시스템** - 눈동자의 움직임만으로 스마트홈을 제어하는 접근성 솔루션> **시선 추적 기반 스마트홈 제어 시스템** - 눈동자의 움직임만으로 스마트홈을 제어하는 접근성 솔루션

- **Dwell Click**: 0.8초 응시로 클릭 (0.3~2.0초 조절 가능)

- **Blink Click**: 0.3~1.0초 깜빡임으로 클릭

- **AI 추천**: 시간/날씨/디바이스 상태 기반 제어 제안

- **WebSocket**: 실시간 시선 위치 스트리밍GazeHome Edge Device는 신체적 장애가 있는 사용자를 위한 혁신적인 접근성 솔루션입니다. 시선과 깜빡임만으로 스마트홈 디바이스를 제어할 수 있으며, AI 기반 추천 시스템이 사용자의 의도를 분석하여 더욱 편리한 제어 경험을 제공합니다.GazeHome Edge Device는 신체적 장애가 있는 사용자를 위한 혁신적인 접근성 솔루션입니다. 시선과 깜빡임만으로 스마트홈 디바이스를 제어할 수 있으며, AI 기반 추천 시스템이 사용자의 의도를 분석하여 더욱 편리한 제어 경험을 제공합니다.

- **Gateway 연동**: aiohttp 기반 디바이스 제어



---

---<p align="center">

## 기술 스택

  <img src="https://via.placeholder.com/800x400?text=GazeHome+Demo+Screenshot" alt="GazeHome Demo" width="800"/>

- **Backend**: FastAPI 0.104.1, uvicorn[standard]

- **Computer Vision**: OpenCV 4.8.1.78, dlib 19.24.2## ✨ 주요 기능</p>

- **Frontend**: Vanilla JavaScript, WebSocket

- **Deployment**: Docker, Docker Compose (ARM64 지원)



---### 🎯 시선 추적 (Gaze Tracking)---



## 프로젝트 구조- **실시간 시선 위치 추적**: dlib 기반 68-point facial landmark 감지



```- **5-Point 보정 시스템**: 화면의 5개 포인트를 활용한 정밀 보정

GazeTracking-master/

├── Dockerfile                       # Docker 컨테이너 설정- **Affine 변환**: 보정 데이터를 활용한 정확한 스크린 좌표 매핑

├── docker-compose.yml               # Docker Compose 설정

├── run_raspberry_pi.sh              # 라즈베리파이 배포 스크립트- **지속성 보정 저장**: JSON 파일로 보정 데이터 저장 및 재사용---

├── requirements.txt                 # Python 의존성

│

├── edge/

│   ├── app.py                      # FastAPI 메인 서버### 👆 이중 클릭 모드## ✨ 주요 기능

│   ├── config.json                 # 설정 파일

│   │- **Dwell Click (응시 클릭)**: 일정 시간(기본 0.8초) 응시로 클릭

│   ├── core/

│   │   ├── config.py               # 설정 관리  - 실시간 진행도 표시 (파란 원)### 🎯 시선 추적 (Gaze Tracking)

│   │   └── database.py             # SQLite DB

│   │  - 조절 가능한 응시 시간 (0.3~2.0초)- **실시간 시선 위치 추적**: dlib 기반 68-point facial landmark 감지

│   ├── gaze/

│   │   ├── tracker.py              # 시선 추적 + 클릭 감지- **Blink Click (깜빡임 클릭)**: 의도적인 깜빡임(0.3~1.0초)으로 클릭- **5-Point 보정 시스템**: 화면의 5개 포인트를 활용한 정밀 보정

│   │   └── calibrator.py           # 5-point 보정

│   │  - 자연스러운 깜빡임 필터링 (< 0.3초)- **Affine 변환**: 보정 데이터를 활용한 정확한 스크린 좌표 매핑

│   ├── model/

│   │   ├── gaze_tracking.py        # dlib 시선 추적 라이브러리  - 눈 감은 시간 추적 및 검증- **지속성 보정 저장**: JSON 파일로 보정 데이터 저장 및 재사용

│   │   ├── eye.py                  # 눈 감지

│   │   ├── pupil.py                # 동공 위치

│   │   └── trained_models/

│   │       └── shape_predictor_68_face_landmarks.dat### 🤖 AI 추천 시스템### 👆 이중 클릭 모드

│   │

│   ├── services/- **컨텍스트 인식**: 시간, 날씨, 디바이스 상태 분석- **Dwell Click (응시 클릭)**: 일정 시간(기본 0.8초) 응시로 클릭

│   │   ├── ai_service.py           # AI 서비스 클라이언트

│   │   └── device_manager.py       # 디바이스 관리- **자동 제어 제안**: AI가 사용자 의도를 분석하여 추천  - 실시간 진행도 표시 (파란 원)

│   │

│   ├── templates/- **YES/NO 응답**: 간단한 응답으로 추천 수락/거부  - 조절 가능한 응시 시간 (0.3~2.0초)

│   │   └── index.html              # 웹 UI

│   │- **실시간 알림**: 팝업 다이얼로그로 추천 표시- **Blink Click (깜빡임 클릭)**: 의도적인 깜빡임(0.3~1.0초)으로 클릭

│   └── static/

│       ├── app.js                  # 프론트엔드 로직  - 자연스러운 깜빡임 필터링 (< 0.3초)

│       └── style.css               # 스타일

│### 🌐 실시간 웹 UI  - 눈 감은 시간 추적 및 검증

├── ai-services-main/                # AI 추천 서비스

└── gateway-main/                    # Gateway 서비스- **WebSocket 기반**: 실시간 양방향 통신

```

- **비디오 스트리밍**: 카메라 영상 오버레이 표시### 🤖 AI 추천 시스템

---

- **시선 포인터**: 녹색 그라데이션 포인터로 시선 위치 시각화- **컨텍스트 인식**: 시간, 날씨, 디바이스 상태 분석

## 설치 및 실행

- **디바이스 카드**: 스마트 디바이스 상태 및 제어 UI- **자동 제어 제안**: AI가 사용자 의도를 분석하여 추천

### 방법 1: Python 직접 실행

- **반응형 디자인**: 다양한 화면 크기 지원- **YES/NO 응답**: 간단한 응답으로 추천 수락/거부

```bash

# 1. 환경 생성- **실시간 알림**: 팝업 다이얼로그로 추천 표시

conda create -n gaze311 python=3.11

conda activate gaze311### 🔌 Gateway 연동



# 2. 의존성 설치- **비동기 HTTP 클라이언트**: aiohttp 기반 효율적인 통신### � 실시간 웹 UI

pip install -r requirements.txt

- **디바이스 관리**: 목록 조회, 상태 확인, 제어 명령 전송- **WebSocket 기반**: 실시간 양방향 통신

# 3. dlib 모델 다운로드

cd edge/model/trained_models/- **주기적 상태 갱신**: 5초마다 자동 상태 업데이트- **비디오 스트리밍**: 카메라 영상 오버레이 표시

wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

bunzip2 shape_predictor_68_face_landmarks.dat.bz2- **Mock 모드**: 테스트를 위한 가상 디바이스 지원- **시선 포인터**: 녹색 그라데이션 포인터로 시선 위치 시각화

cd ../../..

- **디바이스 카드**: 스마트 디바이스 상태 및 제어 UI

# 4. 서버 실행

cd edge---- **반응형 디자인**: 다양한 화면 크기 지원

python app.py

```



브라우저에서 http://localhost:8000 접속## 📁 프로젝트 구조### � Gateway 연동



### 방법 2: Docker 실행- **비동기 HTTP 클라이언트**: aiohttp 기반 효율적인 통신



```bash```- **디바이스 관리**: 목록 조회, 상태 확인, 제어 명령 전송

# 빌드 및 실행

docker-compose up -dGazeTracking-master/- **주기적 상태 갱신**: 5초마다 자동 상태 업데이트



# 로그 확인├── 📄 Dockerfile                    # Docker 컨테이너 설정 (Raspberry Pi 지원)- **Mock 모드**: 테스트를 위한 가상 디바이스 지원

docker-compose logs -f

├── 📄 docker-compose.yml            # Docker Compose 오케스트레이션

# 중지

docker-compose stop├── 📄 run_raspberry_pi.sh           # 라즈베리파이 배포 스크립트---

```

├── 📄 requirements.txt              # Python 의존성 (통합)

### 방법 3: 라즈베리파이 배포├── 📄 .gitignore                    # Git 제외 파일

├── 📄 README.md                     # 프로젝트 문서

```bash│

chmod +x run_raspberry_pi.sh├── 📁 edge/                         # Edge Device 메인 애플리케이션

./run_raspberry_pi.sh│   ├── 📄 app.py                   # FastAPI 메인 서버

```│   ├── 📄 config.json              # 런타임 설정

│   │

---│   ├── 📁 core/                    # 핵심 모듈

│   │   ├── config.py              # 설정 관리자

## 설정 (config.json)│   │   └── database.py            # SQLite 데이터베이스

│   │

```json│   ├── 📁 gaze/                    # 시선 추적 모듈

{│   │   ├── tracker.py             # GazeTracker 메인 로직

    "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",│   │   └── calibrator.py          # 5-point 보정 시스템

    "ai_service_url": "http://localhost:8001",│   │

    "mock_mode": true,│   ├── 📁 model/                   # 시선 추적 ML 모델

    "gaze": {│   │   ├── gaze_tracking.py       # dlib 기반 추적 라이브러리

        "dwell_time": 0.8,│   │   ├── eye.py                 # 눈 감지 알고리즘

        "screen_width": 1920,│   │   ├── pupil.py               # 동공 위치 감지

        "screen_height": 1080,│   │   ├── calibration.py         # 보정 변환 알고리즘

        "camera_index": 0│   │   └── trained_models/

    },│   │       └── shape_predictor_68_face_landmarks.dat

    "polling": {│   │

        "device_status_interval": 5.0,│   ├── 📁 services/                # 외부 서비스 클라이언트

        "recommendation_interval": 3.0│   │   ├── ai_service.py          # AI 서비스 HTTP 클라이언트

    }│   │   └── device_manager.py      # 디바이스 상태 관리

}│   │

```│   ├── 📁 templates/               # 웹 UI 템플릿

│   │   └── index.html             # 메인 SPA

| 파라미터 | 설명 | 기본값 |│   │

|---------|------|--------|│   └── 📁 static/                  # 정적 파일

| `user_uuid` | 사용자 ID | - |│       ├── app.js                 # 프론트엔드 로직

| `ai_service_url` | AI 서비스 URL | `http://localhost:8001` |│       └── style.css              # 스타일시트

| `mock_mode` | Mock 모드 (테스트용) | `false` |│

| `gaze.dwell_time` | Dwell 클릭 시간 (초) | `0.8` |├── 📁 ai-services-main/            # AI 추천 서비스 (별도 프로젝트)

| `gaze.camera_index` | 카메라 인덱스 | `0` |└── 📁 gateway-main/                # Gateway 서비스 (별도 프로젝트)

```

---

---

## API

## 🚀 빠른 시작

### REST API

### 📋 사전 요구사항

- `GET /api/state` - 시스템 상태

- `POST /api/devices/{device_id}/control` - 디바이스 제어- **Python 3.11+**

- `POST /api/calibration/start` - 보정 시작- **웹캠 또는 USB 카메라**

- `GET /api/calibration/progress` - 보정 진행도- **운영체제**: macOS, Linux, Raspberry Pi OS

- `POST /api/dwell-time` - 응시 시간 설정- (선택) Docker & Docker Compose



### WebSocket#### 시스템 패키지 설치



- `ws://localhost:8000/ws` - 실시간 시선 위치 스트리밍<details>

<summary><b>macOS</b></summary>

메시지 타입:

- `gaze`: 시선 위치 `{x, y, pupils_detected}````bash

- `dwell`: 진행도 `{progress: 0.0~1.0}`brew install cmake

- `click`: 클릭 이벤트 `{method: "dwell"|"blink"}````

- `state`: 시스템 상태 업데이트</details>



---<details>

<summary><b>Ubuntu/Debian</b></summary>

## 문제 해결

```bash

### 카메라 열리지 않음sudo apt-get update

```bashsudo apt-get install -y build-essential cmake \

# 카메라 확인    libopencv-dev python3-opencv \

python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"    libopenblas-dev liblapack-dev \

    libx11-dev libgtk-3-dev

# config.json에서 camera_index 수정```

```</details>



### 동공 감지 안 됨<details>

- 조명 밝게 (정면 조명)<summary><b>Raspberry Pi</b></summary>

- 얼굴 화면 정면 위치

- 카메라 거리 40-60cm```bash

sudo apt-get update

### dlib 설치 실패sudo apt-get install -y build-essential cmake \

```bash    python3-opencv libatlas-base-dev \

# macOS    libopenblas-dev liblapack-dev \

brew install cmake    v4l-utils

pip install dlib```

</details>

# Ubuntu

sudo apt-get install cmake libboost-all-dev---

pip install dlib

### 🐍 방법 1: Python 직접 실행 (개발용)

# Raspberry Pi (1-2시간 소요)

pip install dlib --extra-index-url https://www.piwheels.org/simple#### 1️⃣ 환경 설정

```

```bash

---# Conda 환경 생성 (권장)

conda create -n gaze311 python=3.11

## 성능conda activate gaze311



| 환경 | FPS | 메모리 |# 또는 venv 사용

|------|-----|--------|python3 -m venv venv

| PC | 30 FPS | ~300MB |source venv/bin/activate  # Windows: venv\Scripts\activate

| 라즈베리파이 4 | 15-20 FPS | ~300MB |```

| 라즈베리파이 3 | 10-15 FPS | ~300MB |

#### 2️⃣ 의존성 설치

---

```bash

## 라이선스# 프로젝트 클론

git clone https://github.com/yourusername/gazehome-edge.git

접근성 향상을 목표로 개발된 프로젝트입니다.cd gazehome-edge



---# Python 패키지 설치

pip install -r requirements.txt

## 크레딧```



- [GazeTracking](https://github.com/antoinelame/GazeTracking) - 시선 추적 라이브러리#### 3️⃣ dlib 모델 다운로드

- [dlib](http://dlib.net/) - 얼굴 랜드마크 감지

- [FastAPI](https://fastapi.tiangolo.com/) - 웹 프레임워크```bash

- [OpenCV](https://opencv.org/) - 컴퓨터 비전# 모델 디렉토리로 이동

cd edge/model/trained_models/

# 모델 다운로드 및 압축 해제
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2

cd ../../..
```

#### 4️⃣ 설정 파일 편집

`edge/config.json` 파일을 수정하세요:

```json
{
    "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
    "ai_service_url": "http://localhost:8001",
    "mock_mode": true,  // 테스트: true, 프로덕션: false
    "gaze": {
        "dwell_time": 0.8,
        "screen_width": 1920,
        "screen_height": 1080,
        "camera_index": 0
    },
    "polling": {
        "device_status_interval": 5.0,
        "recommendation_interval": 3.0
    }
}
```

#### 5️⃣ 서버 실행

```bash
cd edge
python app.py
```

브라우저에서 **http://localhost:8000** 접속

---

### 🐳 방법 2: Docker 실행 (배포용)

#### 1️⃣ Docker 설치 확인

```bash
docker --version
docker-compose --version
```

#### 2️⃣ 설정 파일 준비

`edge/config.json` 파일이 존재하는지 확인하세요. 없으면 위의 예시를 참고하여 생성합니다.

#### 3️⃣ Docker Compose로 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose stop

# 완전 삭제
docker-compose down
```

#### 4️⃣ 라즈베리파이 자동 배포

```bash
# 실행 권한 부여
chmod +x run_raspberry_pi.sh

# 스크립트 실행
./run_raspberry_pi.sh
```

스크립트는 자동으로 다음을 수행합니다:
- Docker 및 카메라 확인
- config.json 생성 (없는 경우)
- 이미지 빌드
- 컨테이너 실행
- 실시간 로그 출력

---

## 🎮 사용 방법

### 1️⃣ 시선 보정 (Calibration)

처음 사용 시 반드시 시선 보정을 진행해야 합니다.

1. 웹 UI에서 **"시선 보정 시작"** 버튼 클릭
2. 화면에 나타나는 **빨간 점**을 2-3초간 응시
3. 5개 포인트 × 30샘플 자동 수집
4. 보정 완료 후 `calibration_params.json`에 자동 저장

**보정 팁:**
- ✅ 얼굴을 화면 중앙에 위치
- ✅ 충분한 조명 확보 (정면 조명 권장)
- ✅ 카메라와 40-60cm 거리 유지
- ✅ 안경 착용 시 빛 반사 주의

---

### 2️⃣ 클릭 모드

#### 🔵 Dwell Click (응시 클릭)

가장 주요한 클릭 방식입니다.

1. 제어하고 싶은 **디바이스 카드**를 응시
2. 약 **0.8초** 동안 시선 유지
3. 파란 원이 점점 커지며 **진행도 표시**
4. 시간 완료 시 **자동 클릭**

#### 👁️ Blink Click (깜빡임 클릭)

보조 클릭 방식입니다.

1. 대상을 보면서 **의도적으로 눈 감기**
2. **0.3~1.0초** 사이의 깜빡임만 인식
3. 자연스러운 깜빡임(< 0.3초)은 무시

**민감도 조정:**
보정 화면에서 "응시 민감도" 슬라이더로 **0.3~2.0초** 범위 조절 가능

---

### 3️⃣ 디바이스 제어

#### 상태 확인
- 디바이스 카드에 **실시간 상태** 표시
- 🟢 녹색 = ON
- ⚪ 회색 = OFF
- 🔄 5초마다 자동 업데이트

#### 제어 실행
1. 디바이스를 **응시 클릭** 또는 **깜빡임 클릭**
2. AI 서비스가 **사용자 의도 분석**
3. **추천 팝업** 표시
4. **YES** 또는 **NO** 선택

---

### 4️⃣ AI 추천 시스템

AI가 다음 정보를 분석하여 추천합니다:

- ⏰ **시간대**: 아침/점심/저녁
- 🌤️ **날씨**: MCP(Model Context Protocol)를 통한 실시간 날씨 정보
- 📊 **디바이스 상태**: 현재 ON/OFF, 온도 등
- 📈 **사용 패턴**: 과거 제어 히스토리

**예시:**
- 저녁 7시 + 추운 날씨 → "난방을 22도로 켜시겠습니까?"
- 밤 11시 + 조명 켜짐 → "모든 조명을 끄시겠습니까?"

---

## 🔌 API 문서

### REST API 엔드포인트

<details>
<summary><b>GET /api/state</b> - 시스템 상태 조회</summary>

**Response:**
```json
{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "calibrated": true,
  "devices": [
    {
      "device_id": "ac_living_room",
      "name": "거실 에어컨",
      "device_type": "air_conditioner",
      "current_state": {
        "is_on": true,
        "temperature": 24
      }
    }
  ],
  "recommendation": null
}
```
</details>

<details>
<summary><b>POST /api/devices/{device_id}/control</b> - 디바이스 제어</summary>

**Request:**
```json
{
  "action": "toggle",  // "turn_on", "turn_off", "set_temperature"
  "parameters": {
    "temperature": 24  // 선택적
  }
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "ac_living_room",
  "new_state": {
    "is_on": false,
    "temperature": 24
  }
}
```
</details>

<details>
<summary><b>POST /api/calibration/start</b> - 보정 시작</summary>

**Response:**
```json
{
  "status": "started",
  "total_targets": 5,
  "samples_per_target": 30
}
```
</details>

<details>
<summary><b>GET /api/calibration/progress</b> - 보정 진행 상황</summary>

**Response:**
```json
{
  "is_complete": false,
  "current_target": 2,
  "total_targets": 5,
  "current_samples": 15,
  "required_samples": 30,
  "target_position": [960, 540]
}
```
</details>

<details>
<summary><b>POST /api/dwell-time</b> - 응시 시간 설정</summary>

**Request:**
```json
{
  "dwell_time": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "dwell_time": 0.8
}
```
</details>

---

### WebSocket API

실시간 양방향 통신을 위한 WebSocket 엔드포인트: `ws://localhost:8000/ws`

#### 서버 → 클라이언트 메시지

<details>
<summary><b>gaze</b> - 시선 위치 업데이트</summary>

```json
{
  "type": "gaze",
  "position": {"x": 960, "y": 540},
  "pupils_detected": true,
  "timestamp": 1234567890.123
}
```
</details>

<details>
<summary><b>dwell</b> - Dwell 진행도</summary>

```json
{
  "type": "dwell",
  "progress": 0.65,  // 0.0 ~ 1.0
  "position": {"x": 960, "y": 540}
}
```
</details>

<details>
<summary><b>click</b> - 클릭 이벤트</summary>

```json
{
  "type": "click",
  "method": "dwell",  // "dwell" or "blink"
  "position": {"x": 960, "y": 540},
  "device_id": "ac_living_room"  // AOI 매핑 성공 시
}
```
</details>

<details>
<summary><b>state</b> - 시스템 상태 업데이트</summary>

```json
{
  "type": "state",
  "calibrated": true,
  "devices": [...],
  "recommendation": {...}
}
```
</details>

---

### Gateway API 통합

Edge Device는 AI Service를 통해 Gateway와 통신합니다.

**데이터 흐름:**
```
Edge Device → AI Service (Port 8001) → Gateway → Smart Device
```

**Mock 모드:**
- `mock_mode: true`: 가상 디바이스로 UI 테스트
- `mock_mode: false`: 실제 Gateway 연동

---

## ⚙️ 설정 레퍼런스

| 파라미터                          | 설명                         | 기본값                                   |
| --------------------------------- | ---------------------------- | ---------------------------------------- |
| `user_uuid`                       | 사용자 고유 식별자           | `"8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99"` |
| `ai_service_url`                  | AI 서비스 URL                | `"http://localhost:8001"`                |
| `mock_mode`                       | Mock 모드 활성화 (테스트용)  | `false`                                  |
| `gaze.dwell_time`                 | Dwell 클릭 응시 시간 (초)    | `0.8`                                    |
| `gaze.screen_width`               | 화면 너비 (픽셀)             | `1920`                                   |
| `gaze.screen_height`              | 화면 높이 (픽셀)             | `1080`                                   |
| `gaze.camera_index`               | 카메라 디바이스 인덱스       | `0`                                      |
| `polling.device_status_interval`  | 디바이스 상태 갱신 주기 (초) | `5.0`                                    |
| `polling.recommendation_interval` | AI 추천 폴링 주기 (초)       | `3.0`                                    |

---

## 🐛 문제 해결

### ❌ 카메라가 열리지 않음

```bash
# 사용 가능한 카메라 확인
python -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"

# config.json에서 camera_index 수정
```

**Docker 사용 시:**
```bash
# 카메라 권한 확인
ls -l /dev/video*

# 권한 부여
sudo chmod 666 /dev/video0
sudo usermod -aG video $USER
```

---

### ❌ 동공 감지 안 됨 (pupils_detected=False)

**원인:**
- 조명 부족
- 얼굴 각도
- 카메라 거리

**해결:**
- ✅ 조명을 **밝게** 조정 (정면 조명 권장)
- ✅ 얼굴을 **화면 정면**에 위치
- ✅ 카메라와 **40-60cm** 거리 유지
- ✅ 안경 착용 시 **빛 반사** 각도 조정

---

### ❌ WebSocket 연결 끊김

```bash
# uvicorn[standard] 재설치
pip install --upgrade 'uvicorn[standard]'

# 방화벽 확인
sudo ufw allow 8000
```

---

### ❌ dlib 설치 실패

<details>
<summary><b>macOS</b></summary>

```bash
brew install cmake
pip install dlib
```
</details>

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt-get install cmake libboost-all-dev
pip install dlib
```
</details>

<details>
<summary><b>Raspberry Pi (오래 걸림: 1-2시간)</b></summary>

```bash
# piwheels 사용 (빠름)
pip install dlib --extra-index-url https://www.piwheels.org/simple

# 또는 소스 빌드 (느림)
sudo apt-get install cmake libboost-all-dev
pip install dlib
```
</details>

---

### ❌ Gateway/AI Service 응답 없음

1. **서버 실행 확인**
   ```bash
   curl http://localhost:8001/health
   curl http://localhost:8000/health
   ```

2. **config.json URL 확인**
   ```json
   {
     "ai_service_url": "http://localhost:8001"
   }
   ```

3. **방화벽 설정**
   ```bash
   sudo ufw allow 8000
   sudo ufw allow 8001
   ```

---

### ❌ 보정이 부정확함

- ✅ **충분한 조명** 확보
- ✅ 보정 중 **머리 고정**
- ✅ **재보정** 수행 ("시선 보정 시작" 다시 클릭)
- ✅ `gaze/calibrator.py`의 `stability_threshold` 조정

```python
# gaze/calibrator.py
STABILITY_THRESHOLD = 30  # 기본값, 높일수록 안정적
```

---

## 📊 성능 최적화

### 라즈베리파이 최적화

#### 1️⃣ 비디오 해상도 줄이기

`edge/app.py` 수정:

```python
# 카메라 읽기 전에 추가
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

#### 2️⃣ 폴링 주기 늘리기

`edge/config.json` 수정:

```json
{
  "polling": {
    "device_status_interval": 10.0,  // 5.0 → 10.0
    "recommendation_interval": 5.0   // 3.0 → 5.0
  }
}
```

#### 3️⃣ 하드웨어 가속 활성화

```bash
# OpenCL 설치 (Raspberry Pi)
sudo apt-get install ocl-icd-libopencl1
```

---

### 메모리 사용량

| 구성요소           | 메모리     |
| ------------------ | ---------- |
| Python + FastAPI   | ~150MB     |
| dlib 모델          | ~100MB     |
| OpenCV + 웹캠 버퍼 | ~50MB      |
| **총합**           | **~300MB** |

---

### 프레임 레이트

| 환경           | FPS       |
| -------------- | --------- |
| 고성능 PC      | 30 FPS    |
| 라즈베리파이 4 | 15-20 FPS |
| 라즈베리파이 3 | 10-15 FPS |

`edge/app.py`에서 조정 가능:

```python
# 프레임 레이트 제한
await asyncio.sleep(1/30)  # 30 FPS
```

---

## 🔒 보안 고려사항

⚠️ **이 프로젝트는 데모 구현체입니다.**

프로덕션 환경에서는 다음을 추가하세요:

- 🔐 **인증 시스템**: JWT 토큰 기반 사용자 인증
- 🔒 **HTTPS**: SSL/TLS 암호화 통신
- 🛡️ **CORS 제한**: 허용된 도메인만 접근
- 📦 **보정 데이터 암호화**: `calibration_params.json` 암호화
- 🚦 **Rate Limiting**: API 호출 제한
- 🔑 **WebSocket 인증**: 토큰 기반 WebSocket 연결

---

## 📝 데이터 흐름

```
1. 카메라 → 시선 추적 → 보정 변환 → 스크린 좌표

2. 스크린 좌표 → Dwell 감지 → 클릭 이벤트

3. 클릭 이벤트 → AOI 매핑 → 디바이스 ID + 액션

4. 디바이스 정보 → AI 서비스 → 의도 분석 → 추천

5. 추천 → 사용자 (YES/NO) → AI 서비스 응답

6. YES → Gateway 제어 → 디바이스 상태 업데이트 → UI 갱신
```

---

## 🧪 테스트

### Mock 모드 테스트

`edge/config.json`에서 `mock_mode: true` 설정 후:

```bash
cd edge
python app.py
```

**Mock 모드 기능:**
- 가상 디바이스 3개 (에어컨, 조명, 온도조절기)
- AI 추천 시뮬레이션
- Gateway 없이 UI 테스트 가능

---

### 브랜치별 모드

```bash
# 테스트 브랜치 (Mock 모드)
git checkout test
git checkout test2

# 프로덕션 브랜치 (Real 모드)
git checkout main
```

---

## 🚀 배포 가이드

### Raspberry Pi 배포

1. **Docker 설치**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Docker Compose 설치**
   ```bash
   sudo apt-get install docker-compose
   ```

3. **프로젝트 클론**
   ```bash
   git clone https://github.com/yourusername/gazehome-edge.git
   cd gazehome-edge
   ```

4. **자동 배포**
   ```bash
   chmod +x run_raspberry_pi.sh
   ./run_raspberry_pi.sh
   ```

5. **접속**
   ```
   http://<raspberry-pi-ip>:8000
   ```

---

### Systemd 서비스 등록 (자동 시작)

```bash
sudo tee /etc/systemd/system/gazehome-edge.service > /dev/null <<EOF
[Unit]
Description=GazeHome Edge Device
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/edge/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable gazehome-edge.service
sudo systemctl start gazehome-edge.service

# 상태 확인
sudo systemctl status gazehome-edge.service
```

---

## 🤝 기여하기

이슈 및 Pull Request를 환영합니다!

### 개발 환경 설정

```bash
# 레포지토리 포크 후 클론
git clone https://github.com/yourusername/gazehome-edge.git
cd gazehome-edge

# 개발 브랜치 생성
git checkout -b feature/my-feature

# 의존성 설치
pip install -r requirements.txt

# 커밋 및 푸시
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

---

## 🎓 향후 개선 계획

- [ ] **WebSocket 기반 실시간 추천** (폴링 대체)
- [ ] **멀티유저 지원** (얼굴 인식)
- [ ] **음성 확인** (추천에 대한 음성 응답)
- [ ] **제스처 명령** (고개 끄덕임, 흔들기)
- [ ] **오프라인 모드** (캐시된 추천)
- [ ] **PWA 지원** (모바일 접근)
- [ ] **분석 대시보드** (사용 패턴 시각화)
- [ ] **커스텀 AOI 편집기** (사용자 정의 영역)

---

## 📄 라이선스

이 프로젝트는 접근성 향상을 목표로 개발되었습니다.  
자세한 라이선스는 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 🙏 크레딧

- **[GazeTracking](https://github.com/antoinelame/GazeTracking)** - 기본 시선 추적 라이브러리
- **[dlib](http://dlib.net/)** - 얼굴 랜드마크 감지
- **[FastAPI](https://fastapi.tiangolo.com/)** - 웹 프레임워크
- **[OpenCV](https://opencv.org/)** - 컴퓨터 비전 라이브러리

---

## 📞 문의

문제가 발생하면 [GitHub Issues](https://github.com/yourusername/gazehome-edge/issues)에 등록해주세요.

---

<p align="center">
  <b>Built with ❤️ for Accessibility</b><br>
  <i>GazeHome Project</i>
</p>
