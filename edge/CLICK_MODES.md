# 클릭 감지 방식

## 개요
GazeHome Edge Device는 **두 가지 클릭 방식을 동시에 지원**합니다:
1. **Dwell-time (응시 시간)**: 특정 영역을 일정 시간 응시하면 클릭
2. **Blink (눈 깜빡임)**: 의도적으로 눈을 깜빡이면 클릭

**두 방식 모두 항상 활성화**되어 있으며, 사용자는 원하는 방식을 자유롭게 사용할 수 있습니다.

---

## 1. Dwell-time 클릭 (응시 시간)

### 작동 방식
1. 특정 영역(기기 카드)에 시선 고정
2. 시선이 30px 이내로 유지됨
3. 설정된 시간(기본 0.8초) 경과
4. ✅ 클릭 발생

### 특징
- **정확성**: 의도하지 않은 클릭 방지
- **시각적 피드백**: 파란색 원형 진행 바 표시
- **조정 가능**: 0.3초 ~ 2.0초 범위

### 장점
- 안정적이고 예측 가능
- 진행도를 실시간으로 확인 가능
- 실수로 인한 클릭 방지

### 단점
- 클릭까지 시간이 소요됨
- 빠른 반응이 필요한 경우 불편할 수 있음

---

## 2. Blink 클릭 (눈 깜빡임)

### 작동 방식
1. 원하는 영역(기기 카드)에 시선 고정
2. 의도적으로 눈을 감음
3. 깜빡임 지속시간 0.3~1.0초 체크
4. ✅ 클릭 발생 (깜빡이기 전 응시 위치에서)

### 특징
- **빠른 반응**: 즉각적인 클릭 가능
- **자연스러움**: 일상적인 동작 활용
- **지속시간 필터**: 일반 깜빡임(< 0.3초)과 구분

### 장점
- 매우 빠른 반응 속도
- 직관적이고 자연스러운 인터랙션
- 응시 시간이 필요 없음

### 단점
- 조명 환경에 민감할 수 있음
- 의도하지 않은 깜빡임 주의 필요
- 일반 깜빡임과 의도적 깜빡임 구분 필요

### 감지 조건
```python
# 클릭으로 인식되는 깜빡임 조건
0.3초 ≤ 깜빡임 지속시간 ≤ 1.0초

# 무시되는 경우
- 0.3초 미만: 일반적인 무의식 깜빡임
- 1.0초 초과: 너무 긴 눈 감음 (피로 등)
```

---

## 사용 가이드

### 응시 시간 조정
- UI 슬라이더: 0.3초 ~ 2.0초
- 기본값: 0.8초
- 개인의 편의에 맞게 조정

### 클릭 방법 선택
사용자는 **상황에 따라 자유롭게 선택**:

#### Dwell (응시) 사용 시
```
1. 기기 카드에 시선 고정
2. 파란 원형 진행 바 확인
3. 설정 시간 경과 시 자동 클릭
```

#### Blink (깜빡임) 사용 시
```
1. 기기 카드에 시선 고정
2. 의도적으로 천천히 깜빡임 (0.3~1.0초)
3. 즉시 클릭 발생
```

### 추천 사용법
- **정확한 제어**: Dwell 방식 사용
- **빠른 제어**: Blink 방식 사용
- **편안한 사용**: 둘을 혼용하여 사용

---

## 시각적 피드백

### 시선 포인터
- **위치**: 웹캠 영상 위
- **색상**: 초록색 원형
- **효과**: 그림자 + 펄스 애니메이션
- **기능**: 현재 응시 지점 표시

### Dwell 진행도
- **위치**: 응시 지점
- **모양**: 파란색 원형 진행 바
- **애니메이션**: 회전 (spin)
- **기능**: 클릭까지 남은 시간 표시

### 클릭 피드백
- **포인터**: 초록 → 빨강 → 초록 (0.2초)
- **기기 카드**: 확대 + 그림자 (0.5초)
- **로그**: 콘솔에 클릭 방식 표시

---

## 기술 구현

### GazeTracker 초기화
```python
tracker = GazeTracker(
    screen_width=1920,
    screen_height=1080,
    dwell_time=0.8,
    click_mode='both'  # 항상 두 방식 모두 활성화
)
```

### 클릭 감지 결과
```python
result = tracker.update(frame)

if result['click_detected']:
    method = result['click_method']  # 'dwell' or 'blink'
    device = result['clicked_device']
    print(f"Click by {method}: {device['device_id']}")
```

### 클릭 감지기

#### DwellClickDetector
```python
class DwellClickDetector:
    def __init__(self, dwell_time=0.8, tolerance=30):
        self.dwell_time = dwell_time  # 응시 시간
        self.tolerance = tolerance     # 허용 오차 (픽셀)
    
    def update(self, x, y) -> Optional[Tuple[int, int]]:
        # 응시 지속 시간 체크
        # tolerance 내에서 유지 시 클릭 반환
```

#### BlinkClickDetector
```python
class BlinkClickDetector:
    def __init__(self, 
                 blink_duration_min=0.3, 
                 blink_duration_max=1.0):
        self.blink_duration_min = blink_duration_min
        self.blink_duration_max = blink_duration_max
    
    def update(self, is_blinking, gaze_position) -> Optional[Tuple[int, int]]:
        # 깜빡임 시작/종료 감지
        # 지속시간 체크 → 범위 내이면 클릭 반환
```

---

## FAQ

### Q: 왜 두 방식을 모두 활성화하나요?
A: 사용자가 상황과 선호에 따라 자유롭게 선택할 수 있도록 하기 위함입니다. 정확성이 필요할 때는 Dwell, 빠른 제어가 필요할 때는 Blink를 사용할 수 있습니다.

### Q: 두 방식이 동시에 감지되면?
A: 먼저 감지된 방식의 클릭이 실행됩니다. 일반적으로 Blink가 더 빠르게 반응합니다.

### Q: 일반 깜빡임도 클릭으로 인식되나요?
A: 아니요. 0.3초 미만의 짧은 깜빡임은 무시됩니다. 의도적으로 천천히 깜빡여야 클릭으로 인식됩니다.

### Q: 응시 시간을 어떻게 조정하나요?
A: 웹 UI의 슬라이더를 사용하거나, API를 통해 조정할 수 있습니다:
```bash
curl -X POST http://localhost:8000/api/dwell-time \
  -H "Content-Type: application/json" \
  -d '{"dwell_time": 1.2}'
```

### Q: 클릭 방식을 비활성화할 수 있나요?
A: 현재는 두 방식이 항상 활성화되어 있습니다. 필요하다면 API를 통해 변경 가능합니다:
```bash
# Dwell만 사용
curl -X POST http://localhost:8000/api/click-mode \
  -H "Content-Type: application/json" \
  -d '{"click_mode": "dwell"}'

# Blink만 사용
curl -X POST http://localhost:8000/api/click-mode \
  -H "Content-Type: application/json" \
  -d '{"click_mode": "blink"}'
```

---

## 성능 최적화

### Dwell 클릭 최적화
- 응시 시간을 개인에 맞게 조정 (0.8초 권장)
- tolerance 값 조정으로 민감도 변경 가능

### Blink 클릭 최적화
- 충분한 조명 환경 권장
- 의도적으로 천천히 깜빡이는 연습
- 피로 시 Dwell 방식 사용 권장

---

## 결론

GazeHome Edge Device는 **Dwell과 Blink 두 가지 클릭 방식을 동시에 지원**하여:
- ✅ 사용자 선택의 자유
- ✅ 상황별 최적의 방식 사용
- ✅ 빠르고 정확한 인터랙션

사용자는 자신의 선호와 상황에 맞는 방식을 자유롭게 선택하여 사용할 수 있습니다.
