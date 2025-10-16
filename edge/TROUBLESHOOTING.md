# 문제 해결 가이드 (Troubleshooting Guide)

## ✅ 해결된 문제

### 1. WebSocket 연결 실패
**증상:**
```
WARNING: No supported WebSocket library detected
GET /ws HTTP/1.1" 404 Not Found
```

**해결:**
```bash
pip3 install 'uvicorn[standard]'
```

### 2. 카메라 미초기화
**증상:**
- 서버 로그에 "Camera Status: CLOSED"
- WebSocket 연결되지만 시선 데이터 없음

**해결:**
`app.py`의 `initialize_services()` 함수에 카메라 초기화 코드 추가:
```python
camera = cv2.VideoCapture(config.camera_index)
```

---

## ⚠️ 현재 문제

### 3. 시선 포인터가 화면에 표시되지 않음

**원인:**
```
Gaze result: position=None, pupils_detected=False
```

**dlib이 눈동자를 감지하지 못하고 있습니다!**

---

## 🔍 진단 방법

### 로그 확인
서버 터미널에서 다음 메시지를 찾으세요:

```bash
# 좋은 신호 ✅
INFO - ✅ Camera opened successfully at index 0
INFO - Camera Status: OPEN
INFO - WebSocket connection opened
INFO - connection open

# 나쁜 신호 ❌
INFO - Gaze result: position=None, pupils_detected=False  # 눈동자 감지 안됨
WARNING - Failed to read frame from camera  # 카메라 읽기 실패
```

### 브라우저 콘솔 확인
F12 → Console 탭에서:

```javascript
// 좋은 신호 ✅
WebSocket connected

// 나쁜 신호 ❌
WebSocket connection failed
WebSocket closed unexpectedly
```

---

## 🎯 눈동자 감지 문제 해결

### 문제: `pupils_detected=False`

#### 1단계: 웹캠 영상 확인

브라우저에서 페이지를 열면 **오른쪽 상단에 웹캠 영상**이 표시됩니다.

**확인사항:**
- [ ] 웹캠 영상이 보이나요?
- [ ] 얼굴이 선명하게 보이나요?
- [ ] 화면이 너무 어둡거나 밝지 않나요?

#### 2단계: 조명 확인

**필요한 조명:**
- 밝은 자연광 또는 실내등
- 얼굴 정면에서 비추는 조명
- 역광(뒷빛) 피하기

**테스트:**
```bash
# 터미널에서 로그 확인
# "pupils_detected=True"가 나타나야 함
```

#### 3단계: 카메라 위치 조정

**최적 위치:**
- 카메라와 눈 높이를 맞추세요
- 카메라로부터 40-60cm 거리
- 얼굴을 정면으로 향하세요
- 안경 착용 시 반사광 주의

#### 4단계: shape_predictor 모델 확인

```bash
# 모델 파일 존재 확인
ls -lh /Users/tommykong/Downloads/GazeTracking-master\ 4/gaze_tracking/trained_models/shape_predictor_68_face_landmarks.dat

# 파일 크기가 99MB 정도여야 함
```

만약 파일이 없다면:
```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/gaze_tracking/trained_models
curl -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

#### 5단계: 다른 카메라 인덱스 시도

맥에는 여러 카메라가 있을 수 있습니다 (내장, 외장, Continuity Camera 등):

```bash
# config.json 수정
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge
nano core/config.json

# camera_index를 변경:
# 0 → 기본 카메라 (보통 내장 카메라)
# 1 → 두 번째 카메라
# 2 → 세 번째 카메라
```

서버 재시작:
```bash
python3 app.py
```

---

## 📊 정상 작동 시 로그

### 서버 시작
```
INFO - Initializing GazeHome Edge Device...
INFO - Opening camera at index 0...
INFO - ✅ Camera opened successfully at index 0
INFO - GazeTracker initialized: 1920x1080
INFO - ✅ Services initialized successfully (2 devices loaded)
INFO - Camera Status: OPEN
INFO - ✅ Server ready at http://localhost:8000
```

### WebSocket 연결
```
INFO - WebSocket connection opened
INFO - connection open
```

### 시선 추적 (100프레임마다)
```
INFO - WebSocket frame 100: Camera=OPEN, GazeTracker=OK
INFO - Gaze result: position=(960, 540), pupils_detected=True  ← 이렇게 나와야 함!
```

### 클릭 감지
```
# Dwell-time 클릭
INFO - Click detected (dwell): ac_living_room at (320, 100)

# Blink 클릭
INFO - Blink click detected: 0.45s
INFO - Click detected (blink): air_purifier_living_room at (800, 100)
```

---

## 🐛 디버깅 팁

### 1. 실시간 로그 모니터링

터미널에서 서버 실행 후 로그를 계속 확인:
```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge
python3 app.py
```

### 2. 브라우저 개발자 도구

F12 → Console 탭:
```javascript
// WebSocket 메시지 확인
// 'gaze' 타입 메시지가 계속 와야 함:
{type: 'gaze', position: {x: 960, y: 540}}

// 'state' 타입 메시지:
{type: 'state', calibrated: true, devices: [...]}
```

### 3. 네트워크 탭 확인

F12 → Network 탭:
- `/ws` → Status 101 (Switching Protocols) ✅
- `/video_feed` → Status 200 OK ✅
- `/api/state` → Status 200 OK ✅

---

## 🔧 고급 디버깅

### 카메라 프레임 직접 테스트

```python
import cv2

# 카메라 열기
camera = cv2.VideoCapture(0)  # 또는 1, 2

if not camera.isOpened():
    print("❌ 카메라를 열 수 없습니다")
else:
    print("✅ 카메라 열림")
    
    # 프레임 읽기
    ret, frame = camera.read()
    
    if ret:
        print(f"✅ 프레임 읽기 성공: {frame.shape}")
        # 프레임 저장
        cv2.imwrite("test_frame.jpg", frame)
        print("test_frame.jpg 저장됨")
    else:
        print("❌ 프레임 읽기 실패")
    
    camera.release()
```

### dlib 얼굴 감지 테스트

```python
import cv2
import dlib

# 얼굴 감지기 초기화
detector = dlib.get_frontal_face_detector()

# 카메라에서 프레임 가져오기
camera = cv2.VideoCapture(0)
ret, frame = camera.read()

if ret:
    # 그레이스케일 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 얼굴 감지
    faces = detector(gray)
    
    print(f"감지된 얼굴 수: {len(faces)}")
    
    if len(faces) > 0:
        print("✅ 얼굴 감지 성공!")
        for i, face in enumerate(faces):
            print(f"  얼굴 {i+1}: {face}")
    else:
        print("❌ 얼굴 감지 실패")
        print("조명을 밝게 하고, 카메라를 정면으로 보세요")

camera.release()
```

---

## 📝 체크리스트

시선 추적이 작동하려면:

- [ ] **WebSocket** 라이브러리 설치됨 (`uvicorn[standard]`)
- [ ] **카메라** 정상 열림 (Camera Status: OPEN)
- [ ] **조명** 충분히 밝음
- [ ] **얼굴** 카메라 정면을 향함
- [ ] **거리** 40-60cm
- [ ] **shape_predictor** 모델 파일 존재 (99MB)
- [ ] **로그**에서 `pupils_detected=True` 확인
- [ ] **브라우저**에서 웹캠 영상 표시됨
- [ ] **시선 포인터** (초록색 점) 화면에 표시됨

---

## 🆘 여전히 안 될 때

### 맥북의 경우

**Continuity Camera 경고:**
```
WARNING: AVCaptureDeviceTypeExternal is deprecated for Continuity Cameras
```

이 경고는 무시해도 됩니다. 카메라는 정상 작동합니다.

### 권한 문제

**시스템 환경설정** → **보안 및 개인정보보호** → **카메라**:
- ✅ **터미널** 앱에 카메라 권한 부여
- ✅ **Python** 앱에 카메라 권한 부여

### 카메라 인덱스 확인

```python
import cv2

# 사용 가능한 카메라 찾기
for i in range(5):
    camera = cv2.VideoCapture(i)
    if camera.isOpened():
        print(f"✅ 카메라 {i} 사용 가능")
        ret, frame = camera.read()
        if ret:
            print(f"   프레임 크기: {frame.shape}")
        camera.release()
    else:
        print(f"❌ 카메라 {i} 사용 불가")
```

---

## 🎉 성공 시나리오

모든 것이 정상 작동하면:

1. **서버 시작:**
   ```
   ✅ Camera opened successfully at index 0
   ✅ Services initialized successfully
   ✅ Server ready at http://localhost:8000
   ```

2. **브라우저 접속:**
   - 웹캠 영상 표시됨 (오른쪽 상단)
   - WebSocket connected 메시지 (콘솔)

3. **시선 보정:**
   - 화면에 나타나는 점들을 차례로 바라보기
   - 각 점마다 3초간 응시
   - 9개 점 완료 후 "보정 완료"

4. **시선 포인터:**
   - **초록색 점**이 시선을 따라 움직임
   - 실시간으로 위치 업데이트

5. **클릭 감지:**
   - **Dwell-time:** 0.8초 응시 시 클릭
   - **Blink:** 0.3~1.0초 깜빡임 시 클릭
   - 장치 영역에 클릭 시 제어 명령 전송

---

## 📞 추가 도움말

문제가 계속되면 다음 정보를 확인하세요:

1. **맥 OS 버전:**
   ```bash
   sw_vers
   ```

2. **Python 버전:**
   ```bash
   python3 --version
   ```

3. **OpenCV 버전:**
   ```bash
   python3 -c "import cv2; print(cv2.__version__)"
   ```

4. **dlib 버전:**
   ```bash
   python3 -c "import dlib; print(dlib.__version__)"
   ```

5. **카메라 정보:**
   ```bash
   system_profiler SPCameraDataType
   ```
