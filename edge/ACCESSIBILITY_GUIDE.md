# 접근성 가이드 - 몸이 불편한 사용자를 위한 시선 제어

## 🎯 대상 사용자
이 시스템은 **신체적 제약으로 인해 손을 사용하기 어려운 사용자**를 위해 설계되었습니다:
- 상지 장애가 있는 사용자
- 근육 질환으로 움직임이 제한된 사용자
- 일시적 부상으로 손을 사용할 수 없는 사용자
- 기타 시선 기반 제어가 필요한 모든 사용자

---

## ✅ 핵심 기능 확인

### 1. 시선 포인터 (Gaze Pointer)
**✅ 구현 완료**

#### 기능
- 사용자가 **바라보는 위치**를 화면에 실시간 표시
- 초록색 원형 포인터로 시각화
- 그림자와 펄스 애니메이션으로 명확한 가시성

#### 작동 확인
```javascript
// static/app.js
function updateGazePointer(data) {
    const pointer = document.getElementById('gaze-pointer');
    if (!data.position) {
        pointer.classList.remove('active');
        return;
    }
    
    const { x, y } = data.position;
    pointer.style.left = `${x}px`;
    pointer.style.top = `${y}px`;
    pointer.classList.add('active');  // ✅ 포인터 표시
}
```

#### 시각적 특징
- **색상**: 초록색 (#00ff00)
- **크기**: 30px 원형
- **효과**: 
  - 그림자 (box-shadow)
  - 펄스 애니메이션 (0.5초 주기)
  - z-index: 100 (항상 최상위)

---

### 2. 눈 깜빡임 클릭 (Blink Click)
**✅ 구현 완료**

#### 기능
사용자가 **원하는 위치를 바라보고 의도적으로 눈을 깜빡이면 클릭**

#### 작동 원리
```python
# gaze/tracker.py - BlinkClickDetector
class BlinkClickDetector:
    def update(self, is_blinking, gaze_position):
        # 1. 깜빡임 시작 감지
        if is_blinking and not self.is_blinking:
            self.blink_start_time = current_time
            self.is_blinking = True
        
        # 2. 깜빡임 종료 감지
        if not is_blinking and self.is_blinking:
            blink_duration = current_time - self.blink_start_time
            
            # 3. 의도적 깜빡임 판단 (0.3~1.0초)
            if 0.3 <= blink_duration <= 1.0:
                return self.last_gaze_position  # ✅ 클릭!
```

#### 감지 조건
| 깜빡임 시간 | 결과   | 이유                      |
| ----------- | ------ | ------------------------- |
| < 0.3초     | 무시   | 일반적인 무의식 깜빡임    |
| 0.3~1.0초   | ✅ 클릭 | 의도적 깜빡임으로 인식    |
| > 1.0초     | 무시   | 너무 긴 눈 감음 (피로 등) |

#### 사용 방법
```
1. 제어하려는 기기를 바라봄 (시선 포인터 확인)
2. 천천히 의도적으로 눈을 깜빡임 (0.3~1.0초)
3. 즉시 클릭 발생!
```

---

### 3. 응시 시간 클릭 (Dwell Click)
**✅ 구현 완료** (추가 옵션)

#### 기능
깜빡임이 어려운 경우, **일정 시간 응시하면 자동 클릭**

#### 작동 원리
```python
# gaze/tracker.py - DwellClickDetector
class DwellClickDetector:
    def update(self, x, y):
        # 1. 시선이 같은 위치에 머무름 (30px 이내)
        if distance <= self.tolerance:
            elapsed = time.time() - self.fixation_start_time
            
            # 2. 설정 시간(0.8초) 경과
            if elapsed >= self.dwell_time:
                return click_position  # ✅ 클릭!
```

#### 진행도 표시
- 파란색 원형 진행 바
- 실시간으로 진행 상황 표시
- 0.8초 경과 시 자동 클릭

---

## 🎨 시각적 피드백 (중요!)

### 1. 시선 위치 표시
```css
.gaze-pointer {
    width: 30px;
    height: 30px;
    border: 3px solid #00ff00;  /* 초록색 테두리 */
    border-radius: 50%;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.8);  /* 그림자 */
    animation: gaze-pulse 0.5s infinite;  /* 펄스 애니메이션 */
}
```

**사용자는 항상 자신이 어디를 보고 있는지 확인 가능**

### 2. 클릭 피드백
```javascript
function handleGazeClick(data) {
    // 포인터 색상 변경: 초록 → 빨강 → 초록
    pointer.style.border = '3px solid #ff0000';
    setTimeout(() => {
        pointer.style.border = '3px solid #00ff00';
    }, 200);
    
    // 기기 카드 하이라이트
    deviceCard.style.transform = 'scale(1.05)';
    deviceCard.style.boxShadow = '0 8px 16px rgba(102, 126, 234, 0.4)';
}
```

**클릭이 성공했을 때 명확한 시각적 피드백 제공**

---

## 📋 실제 사용 시나리오

### 시나리오 1: 에어컨 켜기 (눈 깜빡임 사용)

```
1. 화면에서 "에어컨" 카드 찾기
   └─> 시선 포인터(초록 원)가 실시간으로 따라다님

2. 에어컨 카드로 시선 이동
   └─> 포인터가 에어컨 카드 위치로 이동

3. 천천히 눈 깜빡임 (0.5초 정도)
   └─> 깜빡이는 동안: 마지막 시선 위치 저장
   └─> 눈 뜨는 순간: 클릭 발생!

4. 시각적 피드백 확인
   └─> 포인터 색상: 초록 → 빨강 → 초록
   └─> 에어컨 카드: 크기 확대 + 그림자
   └─> 에어컨 상태 변경 (켜짐/꺼짐)
```

### 시나리오 2: 공기청정기 제어 (응시 시간 사용)

```
1. 공기청정기 카드로 시선 이동
   └─> 시선 포인터가 카드 위로 이동

2. 시선 고정 (움직이지 않고 바라보기)
   └─> 파란색 원형 진행 바 표시
   └─> 진행 바가 점점 채워짐

3. 0.8초 경과
   └─> 자동으로 클릭 발생!

4. 시각적 피드백 확인
   └─> 공기청정기 상태 변경
```

---

## 🔧 개인화 설정

### 응시 시간 조정
```
웹 UI → 슬라이더 이동 → 0.3~2.0초 범위

권장 설정:
- 빠른 제어: 0.5초
- 표준: 0.8초 (기본값)
- 안정적 제어: 1.2초
```

### 두 방식 동시 사용
사용자는 **상황에 따라 자유롭게 선택**:
- **빠른 제어**: 눈 깜빡임
- **정확한 제어**: 응시 시간
- **피로할 때**: 응시 시간 (깜빡임 필요 없음)

---

## ⚠️ 중요 확인 사항

### 1. 웹캠이 계속 작동하는가?
**✅ YES**
```python
# app.py
@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
```
웹캠은 **항상 실행**되며 보정 전/중/후 모두 작동

### 2. 시선 포인터가 웹 화면에 표시되는가?
**✅ YES**
```html
<!-- templates/index.html -->
<div class="video-container">
    <img id="video-feed" src="/video_feed" alt="Camera Feed">
    <div id="gaze-pointer" class="gaze-pointer"></div>  <!-- ✅ -->
</div>
```

### 3. 눈 깜빡임으로 클릭이 되는가?
**✅ YES**
```python
# app.py - 초기화
gaze_tracker = GazeTracker(
    click_mode='both'  # ✅ Dwell + Blink 모두 활성화
)

# gaze/tracker.py - update()
if self.click_mode in ['blink', 'both']:
    blink_click = self.blink_detector.update(is_blinking, gaze_pos)
    if blink_click:
        click_pos = blink_click
        click_method = 'blink'  # ✅
```

### 4. 클릭 피드백이 명확한가?
**✅ YES**
```javascript
// app.js
function handleGazeClick(data) {
    // 1. 포인터 색상 변화
    pointer.style.border = '3px solid #ff0000';
    
    // 2. 기기 카드 하이라이트
    deviceCard.style.transform = 'scale(1.05)';
    deviceCard.style.boxShadow = '0 8px 16px rgba(102, 126, 234, 0.4)';
    
    // 3. 로그 출력
    console.log('Device clicked:', data.device_id);
}
```

---

## 🧪 테스트 방법

### 1. 서버 실행
```bash
cd edge
python app.py
```

### 2. 브라우저 접속
http://localhost:8000

### 3. 시선 보정
```
"시선 보정 시작" 버튼 클릭
→ 5개 빨간 점 순서대로 응시
→ 각 점마다 30개 샘플 수집
→ 보정 완료!
```

### 4. 눈 깨빡임 클릭 테스트
```
1. 에어컨 카드 바라보기
   └─> 초록 포인터가 카드 위에 있는지 확인

2. 천천히 의도적으로 깜빡이기 (0.5초 정도)
   └─> 눈을 감는 시간을 의식적으로 조절

3. 결과 확인
   ✅ 포인터 색상 변화
   ✅ 에어컨 카드 하이라이트
   ✅ 에어컨 상태 변경
   ✅ 콘솔 로그: "Click detected (blink): ac_living_room"
```

### 5. 응시 시간 클릭 테스트
```
1. 공기청정기 카드 바라보기
2. 시선 고정 (움직이지 않기)
3. 파란 진행 바 관찰
4. 0.8초 후 자동 클릭
```

---

## 💡 사용 팁

### 몸이 불편한 사용자를 위한 권장사항

#### 1. 환경 설정
- **조명**: 충분한 조명 확보 (얼굴 인식 정확도 향상)
- **화면 위치**: 편안한 시선 높이
- **웹캠 위치**: 화면 중앙 또는 상단
- **거리**: 웹캠에서 40~60cm 거리

#### 2. 깜빡임 클릭 요령
- **천천히**: 0.3~1.0초 범위 내에서 자연스럽게
- **의도적으로**: 일반 깜빡임보다 살짝 길게
- **연습**: 몇 번 연습하면 자연스러워짐

#### 3. 응시 시간 조정
- **피로도에 따라**: 피곤할 때는 시간을 더 길게 (1.2초)
- **반응 속도**: 빠른 제어가 필요하면 짧게 (0.5초)
- **실수 방지**: 의도하지 않은 클릭이 많으면 길게

#### 4. 두 방식 혼용
- **빠른 제어**: 깜빡임 사용
- **정확한 제어**: 응시 시간 사용
- **피로할 때**: 응시 시간만 사용 (깜빡임 불필요)

---

## 🎉 결론

### ✅ 모든 핵심 기능 구현 완료

1. **시선 포인터** ✅
   - 바라보는 위치를 실시간 표시
   - 초록색 원형 + 그림자 + 애니메이션

2. **눈 깜빡임 클릭** ✅
   - 0.3~1.0초 깜빡임으로 클릭
   - 빠르고 직관적인 제어

3. **응시 시간 클릭** ✅
   - 0.8초 응시로 자동 클릭
   - 깜빡임이 어려울 때 대안

4. **명확한 피드백** ✅
   - 포인터 색상 변화
   - 기기 카드 하이라이트
   - 진행 바 표시

### 🎯 접근성 목표 달성

이 시스템은 **몸이 불편한 사용자가 손을 사용하지 않고 오직 눈으로만 스마트 기기를 제어**할 수 있도록 설계되었습니다:

- ✅ 시선만으로 위치 지정
- ✅ 눈 깜빡임으로 클릭
- ✅ 명확한 시각적 피드백
- ✅ 개인화된 설정

**모든 기능이 정상적으로 구현되어 있습니다!** 🎉
