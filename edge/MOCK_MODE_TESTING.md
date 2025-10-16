# Mock Mode UI 테스트 가이드

Edge Device의 UI를 실제 AI Service나 Gateway 없이 더미 데이터로 테스트하는 방법입니다.

## 📋 목차
1. [Mock 모드란?](#mock-모드란)
2. [설정 방법](#설정-방법)
3. [더미 데이터 구조](#더미-데이터-구조)
4. [UI 테스트 절차](#ui-테스트-절차)
5. [Mock 모드 vs 실제 모드 차이](#mock-모드-vs-실제-모드-차이)

---

## Mock 모드란?

Mock 모드는 **실제 AI Service나 Gateway 서버 없이** Edge Device의 웹 UI를 테스트할 수 있게 해주는 기능입니다.

### 장점
- ✅ AI Service나 Gateway를 실행하지 않아도 됨
- ✅ 네트워크 연결 없이 로컬에서만 테스트 가능
- ✅ 빠른 UI 프로토타이핑 및 디버깅
- ✅ 예측 가능한 더미 데이터로 테스트

### 제약사항
- ⚠️ 실제 기기 제어는 불가능 (상태만 시뮬레이션)
- ⚠️ AI 추천은 사전 정의된 패턴만 가능
- ⚠️ 실제 시스템 통합 테스트는 불가능

---

## 설정 방법

### 1. Mock 모드 활성화

`edge/config.json` 파일에서 `mock_mode`를 `true`로 설정:

```json
{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "ai_service_url": "http://localhost:8001",
  "mock_mode": true,
  "gaze": {
    ...
  }
}
```

### 2. Edge Device 실행

```bash
cd edge
python app.py
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:

```
🎭 Running in MOCK MODE - using dummy data
✅ Services initialized successfully (6 devices loaded)
Mock Mode: True
```

### 3. 브라우저에서 접속

```
http://localhost:8000
```

---

## 더미 데이터 구조

### Mock 기기 목록 (6개)

`mock_data.py`의 `MOCK_DEVICES`에 정의되어 있습니다:

| 기기 ID                | 타입            | 이름        | 초기 상태 | 위치        |
| ---------------------- | --------------- | ----------- | --------- | ----------- |
| light_living_room      | light           | 거실 조명   | ON (80%)  | living_room |
| ac_living_room         | air_conditioner | 거실 에어컨 | OFF       | living_room |
| tv_living_room         | tv              | 거실 TV     | OFF       | living_room |
| speaker_living_room    | speaker         | 거실 스피커 | OFF       | living_room |
| thermostat_living_room | thermostat      | 온도조절기  | 22°C      | living_room |
| light_bedroom          | light           | 침실 조명   | OFF (60%) | bedroom     |

### Mock 추천 시나리오 (3개)

`mock_data.py`의 `MOCK_RECOMMENDATIONS`에 정의:

1. **에어컨 켜기**
   - 트리거: 오후 시간대 감지
   - 메시지: "현재 오후 2시입니다. 에어컨을 시원하게 켜시겠습니까?"
   - 액션: 에어컨을 22°C 냉방 모드로 설정

2. **조명 어둡게 하기**
   - 트리거: 저녁 시간대 밝은 조명
   - 메시지: "조명을 어둡게 하시겠습니까? 영화 감상 모드로 전환합니다."
   - 액션: 조명 밝기를 30%로 낮춤

3. **TV 켜기**
   - 트리거: TV가 꺼진 상태
   - 메시지: "TV를 켜고 볼륨을 적당히 설정하시겠습니까?"
   - 액션: TV를 켜고 볼륨 20, HDMI1 입력으로 설정

---

## UI 테스트 절차

### 테스트 시나리오 1: 기기 목록 표시 확인

1. **브라우저 접속**: `http://localhost:8000`
2. **기대 결과**: 
   - 화면에 6개의 기기 카드가 표시됨
   - 거실 조명은 ON 상태 (파란색)
   - 나머지 기기들은 OFF 상태 (회색)

### 테스트 시나리오 2: 보정(Calibration) 테스트

Mock 모드에서도 실제 카메라를 사용한 보정이 가능합니다.

#### 보정 시작

1. **"Start Calibration" 버튼 클릭**
2. **카메라 권한 허용** (브라우저 팝업)
3. **5개의 포인트 응시**:
   - 빨간 점이 순서대로 표시됩니다
   - 각 점을 3초간 응시하세요
   - 데이터 수집 진행률이 표시됩니다

#### 보정 완료

4. **보정 완료 메시지 확인**
   - "Calibration completed" 메시지
   - 보정 파라미터 저장 (`calibration_params.json`)

#### 보정 없이 테스트 (선택사항)

더미 보정 데이터를 사용하려면 다음 파일을 생성:

**`edge/calibration_params.json`**:
```json
{
  "transform_matrix": [
    [1920, 0, 0],
    [0, 1080, 0]
  ],
  "translation": [0, 0],
  "calibration_points": [
    {"screen": [192, 108], "gaze": [0.1, 0.1]},
    {"screen": [1728, 108], "gaze": [0.9, 0.1]},
    {"screen": [960, 540], "gaze": [0.5, 0.5]},
    {"screen": [192, 972], "gaze": [0.1, 0.9]},
    {"screen": [1728, 972], "gaze": [0.9, 0.9]}
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

### 테스트 시나리오 3: 시선 추적 및 기기 클릭

보정 후 시선 추적을 테스트합니다.

1. **"Start Tracking" 버튼 클릭**
2. **카메라 피드 확인**:
   - 실시간 비디오 스트림 표시
   - 시선 좌표가 화면에 표시
3. **기기 카드 응시**:
   - 거실 조명 카드를 2초간 응시
   - Dwell-time 프로그레스 바가 채워짐
4. **기기 클릭 감지**:
   - 자동으로 기기가 클릭됨
   - Mock 추천 메시지가 표시됨

### 테스트 시나리오 4: Mock 추천 응답

추천 메시지에 응답하는 테스트입니다.

1. **추천 메시지 표시**:
   ```
   현재 오후 2시입니다. 에어컨을 시원하게 켜시겠습니까?
   [Yes] [No]
   ```

2. **"Yes" 버튼 클릭**:
   - 에어컨 상태가 ON으로 변경
   - 온도 22°C로 설정
   - 상태 업데이트 애니메이션

3. **"No" 버튼 클릭**:
   - 추천 거부
   - 기기 상태 변화 없음

### 테스트 시나리오 5: 직접 기기 제어

기기 카드를 클릭하여 직접 제어하는 테스트입니다.

1. **"거실 TV" 카드 응시 및 클릭**
2. **추천 메시지 표시**:
   ```
   TV를 켜고 볼륨을 적당히 설정하시겠습니까?
   [Yes] [No]
   ```
3. **"Yes" 클릭**:
   - TV 상태가 OFF → ON
   - 볼륨 20, HDMI1 입력 설정
   - 카드 색상이 회색 → 파란색으로 변경

### 테스트 시나리오 6: 주기적 추천 (Polling)

Mock 모드에서는 10번의 polling마다 랜덤 추천을 생성합니다.

1. **시선 추적 활성화 상태 유지**
2. **약 30초 대기** (polling_interval: 3초)
3. **자동 추천 팝업 확인**:
   - 3개의 Mock 추천 중 하나가 랜덤으로 표시됨
4. **추천에 응답**:
   - Yes/No 버튼으로 응답
   - 기기 상태 변화 확인

---

## Mock 모드 vs 실제 모드 차이

| 기능              | Mock 모드                 | 실제 모드                       |
| ----------------- | ------------------------- | ------------------------------- |
| **서버 요구사항** | Edge Device만 필요        | AI Service + Gateway 필요       |
| **기기 목록**     | 6개 고정 더미 데이터      | AI Service에서 실제 기기 가져옴 |
| **기기 제어**     | 로컬 상태만 시뮬레이션    | 실제 스마트 기기 제어           |
| **AI 추천**       | 3개 사전 정의 패턴        | AI가 실시간 컨텍스트 분석       |
| **추천 주기**     | 10번 polling당 1회 (30초) | AI Service가 적절한 타이밍 결정 |
| **네트워크**      | 로컬만 사용               | AI Service와 HTTP 통신          |
| **시선 추적**     | 실제 카메라 사용          | 실제 카메라 사용                |
| **보정**          | 실제 카메라 사용          | 실제 카메라 사용                |

---

## Mock 데이터 커스터마이징

### 기기 추가/수정

`edge/mock_data.py` 파일의 `MOCK_DEVICES` 리스트를 편집:

```python
MOCK_DEVICES = [
    {
        "device_id": "my_new_device",
        "device_type": "light",
        "device_name": "내 새 조명",
        "display_name": "내 새 조명",
        "name": "내 새 조명",
        "capabilities": ["on_off", "brightness"],
        "current_state": {
            "is_on": False,
            "brightness": 50
        },
        "location": "bedroom",
        "brand": "Custom"
    },
    # ... 기존 기기들
]
```

### 추천 시나리오 추가

`MOCK_RECOMMENDATIONS` 리스트에 새로운 추천 추가:

```python
MOCK_RECOMMENDATIONS = [
    {
        "recommendation_id": "rec_004",
        "device_id": "my_new_device",
        "prompt_text": "새 조명을 켜시겠습니까?",
        "message": "새 조명을 켜시겠습니까?",
        "action": {
            "device_id": "my_new_device",
            "command": "turn_on",
            "parameters": {
                "brightness": 100
            }
        },
        "intent": "turn_on_light",
        "confidence": 0.90,
        "reasoning": "사용자 정의 추천"
    },
    # ... 기존 추천들
]
```

---

## 문제 해결

### Mock 모드가 활성화되지 않을 때

1. `config.json` 확인:
   ```json
   "mock_mode": true  // false가 아닌지 확인
   ```

2. 서버 재시작:
   ```bash
   # 서버 중지 (Ctrl+C)
   python app.py
   ```

3. 로그 확인:
   ```
   🎭 Running in MOCK MODE - using dummy data
   ```

### 기기 목록이 표시되지 않을 때

1. 브라우저 콘솔(F12) 확인
2. `/api/devices` 엔드포인트 테스트:
   ```bash
   curl http://localhost:8000/api/devices
   ```
3. 더미 데이터 확인:
   ```bash
   python -c "from mock_data import MOCK_DEVICES; print(len(MOCK_DEVICES))"
   ```

### 추천이 표시되지 않을 때

Mock 모드에서는 10번의 polling마다 1번 추천이 표시됩니다.

- **Polling 간격**: 3초
- **추천 주기**: 약 30초마다 1번

더 자주 테스트하려면 `mock_data.py`의 `poll_recommendation` 메서드 수정:

```python
async def poll_recommendation(self):
    self.recommendation_index += 1
    if self.recommendation_index % 3 == 0:  # 10에서 3으로 변경 (9초마다)
        rec = random.choice(MOCK_RECOMMENDATIONS)
        return rec.copy()
    return None
```

---

## 실제 모드로 전환

Mock 모드 테스트 후 실제 시스템 통합 테스트로 전환:

### 1. Mock 모드 비활성화

`config.json`:
```json
{
  "mock_mode": false
}
```

### 2. AI Service 및 Gateway 실행

```bash
# AI Service 실행
cd ai-services-main
docker-compose up -d

# Gateway 실행
cd gateway-main
docker-compose up -d
```

### 3. Edge Device 재시작

```bash
cd edge
python app.py
```

### 4. 실제 연결 확인

로그에서 Mock 모드 메시지가 **없어야** 합니다:
```
✅ Services initialized successfully (X devices loaded)
UUID: 8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99
AI Service: http://localhost:8001
Mock Mode: False  ← 확인!
```

---

## 요약

Mock 모드를 사용하면:
1. ✅ **빠른 UI 개발**: 백엔드 없이 프론트엔드만 테스트
2. ✅ **독립적 테스트**: 네트워크나 외부 서비스 불필요
3. ✅ **예측 가능한 동작**: 더미 데이터로 일관된 테스트
4. ✅ **쉬운 디버깅**: 실제 시스템의 복잡도 제거

실제 통합 테스트 전에 Mock 모드로 UI 완성도를 높이세요! 🎭
