# 🎭 Mock 모드 빠른 시작 가이드

## 1분 안에 UI 테스트 시작하기!

### 📝 단계별 가이드

#### 1️⃣ Mock 모드 활성화 (5초)

```bash
cd edge
```

`config.json` 파일 열어서 한 줄만 수정:
```json
{
  "mock_mode": true
}
```

#### 2️⃣ 서버 실행 (5초)

```bash
python app.py
```

다음 메시지가 보이면 성공:
```
🎭 Running in MOCK MODE - using dummy data
✅ Services initialized successfully (6 devices loaded)
```

#### 3️⃣ 브라우저 열기 (5초)

```
http://localhost:8000
```

#### 4️⃣ UI 확인 (10초)

화면에 6개의 기기 카드가 표시됩니다:
- ✅ 거실 조명 (ON - 파란색)
- ⚪ 거실 에어컨 (OFF - 회색)
- ⚪ 거실 TV (OFF)
- ⚪ 거실 스피커 (OFF)
- ⚪ 온도조절기 (22°C)
- ⚪ 침실 조명 (OFF)

---

## 🎯 주요 테스트 시나리오

### A. 보정(Calibration) 테스트

```
1. "Start Calibration" 버튼 클릭
2. 카메라 권한 허용
3. 빨간 점 5개를 순서대로 3초씩 응시
4. 완료 메시지 확인
```

### B. 시선 추적 + 기기 클릭

```
1. "Start Tracking" 버튼 클릭
2. "거실 에어컨" 카드를 2초간 응시
3. 자동 클릭됨
4. 추천 메시지 표시: "에어컨을 시원하게 켜시겠습니까?"
5. "Yes" 클릭
6. 에어컨 상태가 OFF → ON으로 변경
```

### C. 자동 추천 확인

```
1. 시선 추적 활성화 상태 유지
2. 약 30초 대기
3. 자동 추천 팝업이 나타남 (랜덤)
4. Yes/No로 응답
```

---

## 🔧 Mock 데이터 수정

### 기기 추가

`edge/mock_data.py` 파일의 `MOCK_DEVICES` 리스트에 추가:

```python
{
    "device_id": "fan_bedroom",
    "device_type": "fan",
    "device_name": "침실 선풍기",
    "display_name": "침실 선풍기",
    "name": "침실 선풍기",
    "capabilities": ["on_off", "speed"],
    "current_state": {
        "is_on": False,
        "speed": 2
    },
    "location": "bedroom",
    "brand": "Dyson"
}
```

### 추천 시나리오 추가

`MOCK_RECOMMENDATIONS`에 추가:

```python
{
    "recommendation_id": "rec_004",
    "device_id": "fan_bedroom",
    "prompt_text": "더운 날씨입니다. 선풍기를 켜시겠습니까?",
    "message": "더운 날씨입니다. 선풍기를 켜시겠습니까?",
    "action": {
        "device_id": "fan_bedroom",
        "command": "turn_on",
        "parameters": {"speed": 3}
    },
    "intent": "turn_on_fan",
    "confidence": 0.88,
    "reasoning": "무더운 날씨"
}
```

---

## 🚀 실제 모드로 전환

테스트 완료 후 실제 시스템과 연결:

```json
{
  "mock_mode": false
}
```

그리고 AI Service + Gateway 실행:

```bash
# AI Service
cd ai-services-main
docker-compose up -d

# Gateway
cd gateway-main
docker-compose up -d

# Edge Device
cd edge
python app.py
```

---

## ❓ 문제 해결

### Mock 모드가 안 보여요
- `config.json`에서 `"mock_mode": true` 확인
- 서버 재시작 (`Ctrl+C` 후 `python app.py`)

### 기기 목록이 안 나와요
- 브라우저 새로고침 (F5)
- 콘솔(F12)에서 에러 확인
- `http://localhost:8000/api/devices` 직접 접속

### 추천이 안 나와요
- Mock 모드에서는 **30초마다 1번** 자동 추천
- 기기를 직접 클릭하면 즉시 추천 표시됨

---

## 📚 상세 문서

더 자세한 내용은 다음 문서를 참고하세요:
- [MOCK_MODE_TESTING.md](./MOCK_MODE_TESTING.md) - 전체 가이드
- [README.md](./README.md) - Edge Device 개요
- [DEMO_GUIDE.md](./DEMO_GUIDE.md) - 데모 실행 가이드

---

**Happy Testing! 🎭✨**
