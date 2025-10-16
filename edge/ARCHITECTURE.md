# 🏗️ GazeHome 아키텍처 설명

## 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│              Edge Device (Raspberry Pi)                  │
│                  http://localhost:5000                   │
│  - 웹 UI (브라우저)                                      │
│  - 시선 추적 + 보정                                      │
│  - 비디오 스트리밍                                       │
│  - 시선 클릭 감지                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ HTTP/WebSocket
                   │
          ┌────────▼────────┐
          │   AI Service    │
          │     :8000       │
          │  - 의도 분석    │
          │  - LLM 추천     │
          │  - MCP 통합     │
          └────────┬────────┘
                   │
                   │ HTTP
                   │
          ┌────────▼────────┐
          │    Gateway      │
          │     :8001       │
          │  - 기기 제어    │
          │  - 상태 관리    │
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │   LG ThinQ      │
          │   Smart Devices │
          └─────────────────┘
```

## 통신 흐름

### ❌ 잘못된 구조 (이전)
```
Edge Device ──────> Gateway (직접 통신)
     │
     └─────────────> AI Service
```

### ✅ 올바른 구조 (현재)
```
Edge Device ─────> AI Service ─────> Gateway ─────> Devices
```

## 데이터 플로우

### 1. 기기 목록 조회

```
1. Edge Device
   └─> GET /api/devices (to AI Service)
       └─> AI Service
           └─> GET /v1/devices (to Gateway)
               └─> Gateway
                   └─> Query LG ThinQ API
                       └─> Return device list
                   <─ Device list
           <─ Device list
   <─ Device list (stored in cache)
```

### 2. 시선 클릭 → AI 추천

```
1. User gazes at device card
   └─> Dwell click detected (0.8s)
       └─> Edge Device
           └─> POST /api/gaze/click (to AI Service)
               {
                 "user_id": "uuid",
                 "clicked_device": {...}
               }
               └─> AI Service
                   └─> LLM analyzes intent
                   └─> Generate recommendation
               <─ Recommendation
           <─ Show popup (YES/NO)
```

### 3. YES 응답 → 기기 제어

```
1. User clicks YES
   └─> Edge Device
       └─> POST /v1/intent (to AI Service)
           {
             "answer": "YES",
             "recommendation_id": "..."
           }
           └─> AI Service
               └─> POST /api/devices/control (to AI Service)
                   └─> Forward to Gateway
                       └─> POST /v1/devices/{id}/control
                           └─> Gateway
                               └─> Control LG device
                           <─ Success
                   <─ Updated state
           <─ Result
   <─ UI refresh
```

## 주요 변경 사항

### Edge Device (`edge/app.py`)

**제거됨:**
- ❌ `from api.gateway_client import GatewayClient`
- ❌ `gateway_client = GatewayClient(...)`
- ❌ `await gateway_client.get_devices()`
- ❌ `await gateway_client.control_device(...)`

**변경됨:**
- ✅ 모든 기기 관련 요청이 AI Service를 통해 이루어짐
- ✅ `await ai_client.get_devices()`
- ✅ `await ai_client.control_device(...)`

### AI Service Client (`edge/api/ai_client.py`)

**추가됨:**
```python
async def get_devices() -> List[Dict]:
    """Get devices from AI Service (which queries Gateway)"""
    result = await self._request('GET', '/api/devices', ...)
    return result['devices']

async def control_device(device_id, action, parameters):
    """Control device via AI Service (which forwards to Gateway)"""
    result = await self._request('POST', '/api/devices/control', ...)
    return result
```

### Configuration (`edge/config.json`)

**변경 전:**
```json
{
  "server": {
    "gateway_url": "http://localhost:8001",  // ❌ 제거됨
    "ai_service_url": "http://localhost:8000"
  }
}
```

**변경 후:**
```json
{
  "server": {
    "ai_service_url": "http://localhost:8000"  // ✅ AI Service만 사용
  }
}
```

## 통신 프로토콜

### Edge Device → AI Service

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/gaze/click` | POST | 시선 클릭 이벤트 전송 |
| `/api/devices` | GET | 기기 목록 조회 |
| `/api/devices/control` | POST | 기기 제어 요청 |
| `/v1/intent` | GET | AI 추천 폴링 |
| `/v1/intent` | POST | 추천 응답 (YES/NO) |

### AI Service → Gateway

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/devices` | GET | 기기 목록 조회 |
| `/v1/devices/{id}` | GET | 기기 상세 정보 |
| `/v1/devices/{id}/status` | GET | 기기 상태 조회 |
| `/v1/devices/{id}/control` | POST | 기기 제어 실행 |

## 보안 & 네트워크

### Edge Device (Raspberry Pi)
- **포트:** 5000
- **프로토콜:** HTTP, WebSocket
- **연결 대상:** AI Service만
- **공개:** 로컬 네트워크

### AI Service
- **포트:** 8000
- **프로토콜:** HTTP
- **연결 대상:** Edge Device (from), Gateway (to)
- **역할:** 중개자 + AI 분석

### Gateway
- **포트:** 8001
- **프로토콜:** HTTP
- **연결 대상:** AI Service (from), LG ThinQ API (to)
- **역할:** 기기 제어 브리지

## 단일 UUID 사용

**UUID:** `8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99`

모든 통신에서 동일한 UUID 사용:
- Edge Device → `user_uuid` in config
- AI Service requests → `user_id` field
- Gateway requests → `user_uuid` field
- 추천 저장 → `user_id` key

## 장점

### 보안
- ✅ Edge Device는 AI Service만 신뢰
- ✅ Gateway는 직접 노출되지 않음
- ✅ 중앙 집중식 인증 가능 (AI Service에서)

### 유지보수
- ✅ Edge Device 코드 단순화
- ✅ AI Service가 모든 비즈니스 로직 관리
- ✅ Gateway 변경 시 Edge Device 영향 없음

### 확장성
- ✅ 여러 Edge Device → 하나의 AI Service
- ✅ AI Service가 부하 분산 가능
- ✅ Gateway 클러스터링 용이

## 테스트 방법

### 1. AI Service 엔드포인트 확인
```bash
# 기기 목록 (AI Service를 통해)
curl http://localhost:8000/api/devices?user_id=8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99

# 기기 제어 (AI Service를 통해)
curl -X POST http://localhost:8000/api/devices/control \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
    "device_id": "light_001",
    "action": "toggle"
  }'
```

### 2. Edge Device 동작 확인
```bash
# Edge Device 시작
cd edge
python run.py

# 브라우저에서 http://localhost:5000 접속
# 기기 카드가 표시되는지 확인 (AI Service → Gateway 통신 성공)
```

### 3. 전체 플로우 테스트
1. Edge Device UI에서 기기 카드 응시
2. Dwell click 발생
3. AI 추천 팝업 확인
4. YES 클릭
5. 기기 상태 변경 확인

## 문제 해결

### Edge Device에서 기기 목록이 안 보임
```bash
# AI Service 상태 확인
curl http://localhost:8000/api/gaze/status

# AI Service가 Gateway와 통신하는지 확인
# AI Service 로그 확인
```

### 기기 제어가 안됨
```bash
# AI Service → Gateway 통신 확인
curl http://localhost:8000/api/devices/control -X POST -d '{...}'

# Gateway 상태 확인
curl http://localhost:8001/health
```

---

**요약:** Edge Device는 Gateway와 **직접 통신하지 않고**, 모든 요청을 **AI Service를 통해** 처리합니다.
