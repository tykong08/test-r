# GazeHome Edge Device API 명세서

## 📋 개요

**버전:** 1.0.0  
**Base URL:** `http://<edge-device-ip>:8000`  
**프로토콜:** HTTP/1.1, WebSocket  
**인증:** None (로컬 네트워크 전용)

GazeHome Edge Device는 시선 추적 기반 스마트 홈 제어를 위한 라즈베리파이 엣지 디바이스입니다.

---

## 🔗 엔드포인트 목록

### HTTP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | 메인 웹 UI 페이지 |
| GET | `/video_feed` | 실시간 비디오 스트림 (MJPEG) |
| GET | `/api/devices` | 기기 목록 조회 |
| POST | `/api/calibration/start` | 보정 시작 |
| POST | `/api/calibration/collect` | 보정 데이터 수집 |
| POST | `/api/calibration/complete` | 보정 완료 및 계산 |
| GET | `/api/calibration/status` | 보정 상태 조회 |
| POST | `/api/tracking/start` | 시선 추적 시작 |
| POST | `/api/tracking/stop` | 시선 추적 중지 |
| GET | `/api/recommendation` | 현재 추천 조회 |
| POST | `/api/recommendation/respond` | 추천에 응답 |
| POST | `/api/device/control` | 기기 제어 |

### WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| `/ws/gaze` | 실시간 시선 데이터 스트림 |
| `/ws/events` | 이벤트 알림 스트림 |

---

## 📡 HTTP API 상세

### 1. 메인 페이지

#### `GET /`

웹 기반 UI 페이지를 반환합니다.

**Response:**
- `200 OK` - HTML 페이지

---

### 2. 비디오 스트림

#### `GET /video_feed`

실시간 웹캠 피드 with 시선 오버레이

**Response:**
- `200 OK` - Multipart MJPEG stream
- Content-Type: `multipart/x-mixed-replace; boundary=frame`

**Stream Format:**
```
--frame
Content-Type: image/jpeg

[JPEG binary data]
--frame
...
```

**Overlay Elements:**
- 녹색 원: 현재 시선 위치
- 파란색 원: Dwell-time 진행도 (2초 응시 시 클릭)

---

### 3. 기기 목록 조회

#### `GET /api/devices`

제어 가능한 스마트 기기 목록을 반환합니다.

**Response:**
```json
{
  "devices": [
    {
      "device_id": "ac_living_room",
      "device_type": "air_conditioner",
      "device_name": "거실 에어컨",
      "display_name": "거실 에어컨",
      "name": "거실 에어컨",
      "capabilities": ["on_off", "temperature", "mode", "fan_speed"],
      "current_state": {
        "is_on": false,
        "temperature": 24,
        "mode": "cool",
        "fan_speed": "auto"
      },
      "location": "living_room",
      "brand": "LG"
    },
    {
      "device_id": "air_purifier_living_room",
      "device_type": "air_purifier",
      "device_name": "공기청정기",
      "display_name": "공기청정기",
      "name": "공기청정기",
      "capabilities": ["on_off", "fan_speed", "mode", "air_quality"],
      "current_state": {
        "is_on": false,
        "fan_speed": "auto",
        "mode": "auto",
        "air_quality": "good",
        "pm25": 15
      },
      "location": "living_room",
      "brand": "Coway"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - 성공
- `500 Internal Server Error` - 서버 오류

---

### 4. 보정 시작

#### `POST /api/calibration/start`

5-point 시선 보정 프로세스를 시작합니다.

**Request Body:**
```json
{
  "screen_width": 1920,
  "screen_height": 1080
}
```

**Response:**
```json
{
  "status": "started",
  "num_points": 5,
  "calibration_points": [
    {"x": 192, "y": 108},    // Top-left (10%, 10%)
    {"x": 1728, "y": 108},   // Top-right (90%, 10%)
    {"x": 960, "y": 540},    // Center (50%, 50%)
    {"x": 192, "y": 972},    // Bottom-left (10%, 90%)
    {"x": 1728, "y": 972}    // Bottom-right (90%, 90%)
  ],
  "current_point": 0
}
```

**Status Codes:**
- `200 OK` - 보정 시작됨
- `400 Bad Request` - 잘못된 화면 크기

---

### 5. 보정 데이터 수집

#### `POST /api/calibration/collect`

현재 보정 포인트에서 시선 데이터를 수집합니다.

**Request Body:**
```json
{
  "point_index": 0,
  "screen_position": {
    "x": 192,
    "y": 108
  }
}
```

**Response:**
```json
{
  "status": "collecting",
  "point_index": 0,
  "samples_collected": 25,
  "samples_required": 30,
  "progress": 0.83
}
```

또는 충분한 샘플 수집 후:
```json
{
  "status": "point_complete",
  "point_index": 0,
  "samples_collected": 30,
  "next_point": 1
}
```

**Status Codes:**
- `200 OK` - 데이터 수집 중
- `400 Bad Request` - 잘못된 요청
- `404 Not Found` - 보정 세션 없음

---

### 6. 보정 완료

#### `POST /api/calibration/complete`

수집된 데이터로 보정 변환 행렬을 계산하고 저장합니다.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "completed",
  "calibration_quality": {
    "average_error": 15.5,
    "max_error": 32.1,
    "points_collected": 5,
    "status": "good"
  },
  "transform_matrix": [
    [1920.0, 0.0, 0.0],
    [0.0, 1080.0, 0.0]
  ],
  "saved_to": "calibration_params.json"
}
```

**Calibration Quality Status:**
- `excellent` - 평균 오차 < 20px
- `good` - 평균 오차 < 40px
- `acceptable` - 평균 오차 < 60px
- `poor` - 평균 오차 >= 60px

**Status Codes:**
- `200 OK` - 보정 완료
- `400 Bad Request` - 데이터 부족
- `500 Internal Server Error` - 계산 실패

---

### 7. 보정 상태 조회

#### `GET /api/calibration/status`

현재 보정 상태를 조회합니다.

**Response:**
```json
{
  "is_calibrated": true,
  "calibration_file": "calibration_params.json",
  "calibration_time": "2024-01-15T10:30:00",
  "screen_size": {
    "width": 1920,
    "height": 1080
  },
  "quality": {
    "average_error": 15.5,
    "status": "good"
  }
}
```

또는 보정되지 않은 경우:
```json
{
  "is_calibrated": false,
  "message": "Calibration required"
}
```

**Status Codes:**
- `200 OK` - 성공

---

### 8. 시선 추적 시작

#### `POST /api/tracking/start`

실시간 시선 추적과 dwell-time 클릭 감지를 시작합니다.

**Request Body:**
```json
{
  "dwell_time": 2.0
}
```

**Response:**
```json
{
  "status": "started",
  "dwell_time": 2.0,
  "is_calibrated": true,
  "message": "Gaze tracking started successfully"
}
```

**Status Codes:**
- `200 OK` - 추적 시작됨
- `400 Bad Request` - 보정 필요
- `500 Internal Server Error` - 카메라 오류

---

### 9. 시선 추적 중지

#### `POST /api/tracking/stop`

시선 추적을 중지합니다.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "stopped",
  "message": "Gaze tracking stopped"
}
```

**Status Codes:**
- `200 OK` - 추적 중지됨

---

### 10. 현재 추천 조회

#### `GET /api/recommendation`

AI가 생성한 현재 추천을 조회합니다.

**Response:**
```json
{
  "has_recommendation": true,
  "recommendation": {
    "recommendation_id": "rec_001",
    "device_id": "ac_living_room",
    "prompt_text": "현재 온도가 높습니다. 에어컨을 시원하게 켜시겠습니까?",
    "message": "현재 온도가 높습니다. 에어컨을 시원하게 켜시겠습니까?",
    "action": {
      "device_id": "ac_living_room",
      "command": "turn_on",
      "parameters": {
        "temperature": 22,
        "mode": "cool",
        "fan_speed": "auto"
      }
    },
    "intent": "turn_on_ac",
    "confidence": 0.92,
    "reasoning": "실내 온도가 높고 에어컨이 꺼진 상태"
  }
}
```

또는 추천이 없는 경우:
```json
{
  "has_recommendation": false
}
```

**Status Codes:**
- `200 OK` - 성공

---

### 11. 추천 응답

#### `POST /api/recommendation/respond`

추천에 대한 사용자 응답을 전송합니다.

**Request Body:**
```json
{
  "recommendation_id": "rec_001",
  "answer": "YES",
  "device_id": "ac_living_room"
}
```

**Answer Values:**
- `YES` - 추천 수락
- `NO` - 추천 거부

**Response:**
```json
{
  "status": "accepted",
  "recommendation_id": "rec_001",
  "device_id": "ac_living_room",
  "action_executed": true,
  "result": {
    "device_id": "ac_living_room",
    "executed_action": "turn_on",
    "updated_state": {
      "is_on": true,
      "temperature": 22,
      "mode": "cool",
      "fan_speed": "auto"
    }
  }
}
```

거부한 경우:
```json
{
  "status": "rejected",
  "recommendation_id": "rec_001",
  "message": "Recommendation rejected by user"
}
```

**Status Codes:**
- `200 OK` - 응답 처리됨
- `400 Bad Request` - 잘못된 요청
- `404 Not Found` - 추천 ID 없음

---

### 12. 기기 제어

#### `POST /api/device/control`

기기를 직접 제어합니다 (시선 클릭 또는 수동).

**Request Body:**
```json
{
  "device_id": "ac_living_room",
  "action": "turn_on",
  "parameters": {
    "temperature": 22,
    "mode": "cool"
  },
  "trigger": "gaze_click",
  "gaze_position": {
    "x": 320,
    "y": 100
  }
}
```

**Trigger Types:**
- `gaze_click` - 시선 dwell-time 클릭
- `manual` - 수동 버튼 클릭
- `voice` - 음성 명령 (미래 기능)

**Common Actions:**
- `turn_on` - 기기 켜기
- `turn_off` - 기기 끄기
- `toggle` - 상태 전환
- `set_temperature` - 온도 설정 (에어컨)
- `set_fan_speed` - 팬 속도 설정
- `set_mode` - 모드 설정

**Response:**
```json
{
  "status": "success",
  "device_id": "ac_living_room",
  "action": "turn_on",
  "recommendation": {
    "recommendation_id": "rec_auto_001",
    "prompt_text": "에어컨을 22도로 켜시겠습니까?",
    "action": {
      "device_id": "ac_living_room",
      "command": "turn_on",
      "parameters": {
        "temperature": 22,
        "mode": "cool",
        "fan_speed": "auto"
      }
    }
  }
}
```

**Status Codes:**
- `200 OK` - 제어 성공
- `400 Bad Request` - 잘못된 요청
- `404 Not Found` - 기기 없음
- `500 Internal Server Error` - 제어 실패

---

## 🔌 WebSocket API

### 1. 실시간 시선 데이터

#### `WS /ws/gaze`

실시간 시선 위치 및 클릭 이벤트를 스트리밍합니다.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/gaze');
```

**Message Format (Client → Server):**
```json
{
  "type": "subscribe",
  "events": ["gaze", "click", "dwell"]
}
```

**Message Format (Server → Client):**

**Gaze Position:**
```json
{
  "type": "gaze",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "position": {
    "x": 960,
    "y": 540
  },
  "raw_gaze": {
    "horizontal": 0.5,
    "vertical": 0.5
  },
  "is_calibrated": true
}
```

**Dwell Progress:**
```json
{
  "type": "dwell",
  "timestamp": "2024-01-15T10:30:00.456Z",
  "position": {
    "x": 320,
    "y": 100
  },
  "progress": 0.75,
  "device_id": "ac_living_room"
}
```

**Click Event:**
```json
{
  "type": "click",
  "timestamp": "2024-01-15T10:30:02.000Z",
  "position": {
    "x": 320,
    "y": 100
  },
  "device_id": "ac_living_room",
  "device_name": "거실 에어컨"
}
```

**Update Rate:** ~30 Hz (30 messages/second)

---

### 2. 이벤트 알림

#### `WS /ws/events`

시스템 이벤트와 알림을 스트리밍합니다.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');
```

**Message Format (Server → Client):**

**Recommendation Event:**
```json
{
  "type": "recommendation",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "recommendation": {
    "recommendation_id": "rec_001",
    "message": "현재 온도가 높습니다. 에어컨을 켜시겠습니까?",
    "device_id": "ac_living_room"
  }
}
```

**Device State Change:**
```json
{
  "type": "device_state_change",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "device_id": "ac_living_room",
  "old_state": {
    "is_on": false
  },
  "new_state": {
    "is_on": true,
    "temperature": 22
  }
}
```

**Calibration Complete:**
```json
{
  "type": "calibration_complete",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "quality": "good",
  "average_error": 15.5
}
```

**Error Event:**
```json
{
  "type": "error",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "error": "Camera connection lost",
  "severity": "high"
}
```

---

## 📊 데이터 모델

### Device Object

```typescript
interface Device {
  device_id: string;           // 고유 기기 ID
  device_type: string;         // 기기 타입 (air_conditioner, air_purifier, etc.)
  device_name: string;         // 기기 이름
  display_name: string;        // UI 표시 이름
  name: string;                // 별칭
  capabilities: string[];      // 지원 기능 목록
  current_state: object;       // 현재 상태
  location: string;            // 위치
  brand: string;               // 제조사
}
```

### Recommendation Object

```typescript
interface Recommendation {
  recommendation_id: string;   // 고유 추천 ID
  device_id: string;           // 대상 기기 ID
  prompt_text: string;         // 사용자에게 표시할 메시지
  message: string;             // 추천 메시지
  action: {
    device_id: string;
    command: string;           // 실행할 명령
    parameters: object;        // 명령 파라미터
  };
  intent: string;              // 추천 의도
  confidence: number;          // 신뢰도 (0-1)
  reasoning: string;           // 추천 이유
}
```

### Calibration Point

```typescript
interface CalibrationPoint {
  x: number;                   // 화면 X 좌표 (픽셀)
  y: number;                   // 화면 Y 좌표 (픽셀)
}
```

### Gaze Position

```typescript
interface GazePosition {
  x: number;                   // 화면 X 좌표 (픽셀)
  y: number;                   // 화면 Y 좌표 (픽셀)
  horizontal: number;          // 원시 수평 비율 (0-1)
  vertical: number;            // 원시 수직 비율 (0-1)
}
```

---

## 🔐 보안 고려사항

### 현재 구현
- ✅ 로컬 네트워크만 접근 (0.0.0.0:8000)
- ✅ CORS 비활성화 (로컬 전용)
- ❌ 인증 없음
- ❌ HTTPS 없음

### 프로덕션 권장사항
- 🔒 JWT 토큰 기반 인증 추가
- 🔒 HTTPS/WSS 사용
- 🔒 Rate limiting 적용
- 🔒 CORS 정책 설정
- 🔒 방화벽 규칙 설정

---

## 🚀 사용 예제

### JavaScript (Browser)

```javascript
// 1. 기기 목록 조회
fetch('http://localhost:8000/api/devices')
  .then(res => res.json())
  .then(data => {
    console.log('Devices:', data.devices);
  });

// 2. 보정 시작
fetch('http://localhost:8000/api/calibration/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    screen_width: window.screen.width,
    screen_height: window.screen.height
  })
})
  .then(res => res.json())
  .then(data => {
    console.log('Calibration started:', data);
  });

// 3. WebSocket 시선 데이터
const gazeWs = new WebSocket('ws://localhost:8000/ws/gaze');

gazeWs.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'gaze') {
    console.log('Gaze at:', data.position);
  } else if (data.type === 'click') {
    console.log('Clicked device:', data.device_id);
  }
};

// 4. 추천에 응답
fetch('http://localhost:8000/api/recommendation/respond', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    recommendation_id: 'rec_001',
    answer: 'YES',
    device_id: 'ac_living_room'
  })
})
  .then(res => res.json())
  .then(data => {
    console.log('Response:', data);
  });
```

### Python

```python
import requests
import json

BASE_URL = 'http://localhost:8000'

# 1. 기기 목록 조회
response = requests.get(f'{BASE_URL}/api/devices')
devices = response.json()['devices']
print(f'Found {len(devices)} devices')

# 2. 기기 제어
control_data = {
    'device_id': 'ac_living_room',
    'action': 'turn_on',
    'parameters': {
        'temperature': 22,
        'mode': 'cool'
    },
    'trigger': 'manual'
}

response = requests.post(
    f'{BASE_URL}/api/device/control',
    json=control_data
)
result = response.json()
print('Control result:', result)
```

### cURL

```bash
# 기기 목록 조회
curl http://localhost:8000/api/devices

# 보정 시작
curl -X POST http://localhost:8000/api/calibration/start \
  -H "Content-Type: application/json" \
  -d '{"screen_width": 1920, "screen_height": 1080}'

# 추천 응답
curl -X POST http://localhost:8000/api/recommendation/respond \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "rec_001",
    "answer": "YES",
    "device_id": "ac_living_room"
  }'
```

---

## 📝 변경 이력

### v1.0.0 (2024-01-15)
- ✅ 초기 API 릴리스
- ✅ 5-point 보정 시스템
- ✅ Dwell-time 클릭 감지
- ✅ 실시간 WebSocket 스트리밍
- ✅ Mock 모드 지원

---

## 📞 지원

**문서:** [README.md](./README.md)  
**라즈베리파이 설정:** [RASPBERRY_PI_SETUP.md](./RASPBERRY_PI_SETUP.md)  
**Mock 테스트:** [QUICK_START_MOCK.md](./QUICK_START_MOCK.md)

---

**Last Updated:** 2024-01-15  
**API Version:** 1.0.0
