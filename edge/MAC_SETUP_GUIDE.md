# 맥(Mac)에서 설정 가이드

## ⚠️ 현재 문제

맥에서 실행 시 **WebSocket 라이브러리가 없어서** 다음 기능들이 작동하지 않습니다:
- ❌ 시선 포인터 실시간 표시
- ❌ 눈 깜빡임 클릭 이벤트
- ❌ Dwell-time 진행도 표시

### 에러 로그
```
WARNING:  No supported WebSocket library detected.
WARNING:  Please use "pip install 'uvicorn[standard]'", or install 'websockets' or 'wsproto' manually.
INFO:     127.0.0.1:62742 - "GET /ws HTTP/1.1" 404 Not Found
```

---

## ✅ 해결 방법

### 1. WebSocket 라이브러리 설치

```bash
# 방법 1: uvicorn[standard] 설치 (권장)
pip3 install 'uvicorn[standard]'

# 또는 방법 2: websockets 직접 설치
pip3 install websockets

# 또는 방법 3: wsproto 설치
pip3 install wsproto
```

### 2. 설치 확인

```bash
python3 -c "import websockets; print('WebSocket OK')"
# 또는
python3 -c "import wsproto; print('wsproto OK')"
```

### 3. 서버 재시작

```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge
python3 app.py
```

### 4. 정상 작동 확인

서버 로그에서 다음 메시지가 **없어야** 합니다:
```
WARNING:  No supported WebSocket library detected.  ← 이 메시지가 없어야 함!
```

브라우저 콘솔(F12)에서 다음 메시지 확인:
```javascript
WebSocket connected  ← 이 메시지가 있어야 함!
```

---

## 🎯 라즈베리파이와의 차이점

### 라즈베리파이에서는 잘 작동하는 이유

1. **Raspberry Pi OS**는 Python 환경이 완전히 설정되어 있음
2. `requirements.txt` 설치 시 모든 의존성이 자동으로 설치됨
3. WebSocket 라이브러리가 기본 포함될 가능성이 높음

### 맥에서 문제가 발생하는 이유

1. **맥의 Python 환경**은 최소한의 패키지만 설치됨
2. `uvicorn`만 설치하면 WebSocket 지원이 포함되지 않음
3. `uvicorn[standard]` 또는 별도로 WebSocket 라이브러리 설치 필요

---

## 📋 완전한 설치 가이드 (맥)

### 1단계: 가상 환경 생성 (권장)

```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge

# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate
```

### 2단계: 모든 의존성 설치

```bash
# requirements.txt 수정 필요
pip install --upgrade pip
pip install 'uvicorn[standard]'
pip install fastapi
pip install opencv-python
pip install dlib
pip install numpy
pip install scipy
pip install aiohttp
```

### 3단계: dlib 설치 (중요!)

dlib은 특별한 처리가 필요할 수 있습니다:

```bash
# Homebrew 설치 (아직 없다면)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# cmake 설치
brew install cmake

# dlib 설치
pip install dlib
```

만약 dlib 설치가 실패하면:

```bash
# XCode Command Line Tools 설치
xcode-select --install

# 다시 시도
pip install dlib
```

### 4단계: shape_predictor 모델 다운로드

```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/gaze_tracking/trained_models

# 모델이 없다면 다운로드
curl -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### 5단계: 웹캠 권한 설정

맥에서는 웹캠 접근 권한이 필요합니다:

1. **시스템 환경설정** → **보안 및 개인정보보호** → **카메라**
2. **터미널** 또는 **Python** 앱에 카메라 권한 부여

### 6단계: 서버 실행

```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge
python3 app.py
```

### 7단계: 브라우저 테스트

```
http://localhost:8000
```

브라우저 콘솔(F12 → Console)에서 확인:
```javascript
WebSocket connected  // ✅ 이 메시지가 보여야 함
```

---

## 🔍 문제 해결

### 문제 1: WebSocket 연결 실패

**증상:**
```
WARNING: No supported WebSocket library detected
GET /ws HTTP/1.1" 404 Not Found
```

**해결:**
```bash
pip3 install 'uvicorn[standard]'
# 또는
pip3 install websockets
```

### 문제 2: 웹캠 접근 거부

**증상:**
```
Failed to read frame
camera.read() returns False
```

**해결:**
- 시스템 환경설정에서 카메라 권한 부여
- 다른 앱이 웹캠을 사용 중이지 않은지 확인
- 외장 웹캠 사용 시 USB 연결 확인

### 문제 3: dlib 설치 실패

**증상:**
```
error: command 'clang' failed
fatal error: 'Python.h' file not found
```

**해결:**
```bash
# XCode Command Line Tools 설치
xcode-select --install

# cmake 설치
brew install cmake

# Python 개발 헤더 확인
python3-config --includes

# 재시도
pip3 install dlib
```

### 문제 4: OpenCV 카메라 인덱스 오류

**증상:**
```
Cannot open camera at index 0
```

**해결:**
```python
# config.json 수정
{
    "camera_index": 1  // 0 대신 1이나 2 시도
}
```

또는 터미널에서 확인:
```bash
python3 -c "import cv2; print([i for i in range(5) if cv2.VideoCapture(i).isOpened()])"
```

---

## 📊 맥 vs 라즈베리파이 비교

| 항목 | 맥 (Mac) | 라즈베리파이 (Raspberry Pi) |
|-----|---------|----------------------------|
| **Python 환경** | 시스템 Python (최소 설치) | Raspberry Pi OS (완전 설치) |
| **WebSocket** | 별도 설치 필요 ⚠️ | requirements.txt로 자동 설치 ✅ |
| **웹캠 접근** | 시스템 권한 필요 | 자동 허용 |
| **dlib 설치** | XCode + cmake 필요 | apt-get으로 간단 설치 |
| **성능** | 고성능 (개발/테스트용) | 저전력 (실제 배포용) |
| **웹 브라우저** | 최신 브라우저 (Safari, Chrome) | Chromium (기본) |

---

## ✅ 최종 체크리스트

### 맥에서 정상 작동하려면:

- [ ] `uvicorn[standard]` 또는 `websockets` 설치
- [ ] 모든 Python 패키지 설치 (opencv-python, dlib, numpy, scipy, aiohttp)
- [ ] shape_predictor 모델 다운로드
- [ ] 웹캠 권한 부여
- [ ] 서버 실행 시 WebSocket 경고 메시지 없음
- [ ] 브라우저에서 "WebSocket connected" 확인
- [ ] 웹캠 영상 표시 확인
- [ ] 시선 포인터 실시간 표시 확인

---

## 🚀 빠른 설치 스크립트 (맥용)

```bash
#!/bin/bash
# mac-setup.sh

echo "🍎 맥용 GazeHome Edge Device 설정 시작..."

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate

# 필수 패키지 업그레이드
pip install --upgrade pip setuptools wheel

# 모든 의존성 설치
pip install 'uvicorn[standard]'
pip install fastapi
pip install opencv-python
pip install numpy
pip install scipy
pip install aiohttp

# dlib 설치 (실패 시 수동 설치 필요)
echo "📦 dlib 설치 중... (시간이 걸릴 수 있습니다)"
pip install dlib || echo "⚠️ dlib 설치 실패 - 수동 설치 필요"

# shape_predictor 모델 다운로드
cd ../gaze_tracking/trained_models
if [ ! -f "shape_predictor_68_face_landmarks.dat" ]; then
    echo "📥 shape_predictor 모델 다운로드 중..."
    curl -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    bunzip2 shape_predictor_68_face_landmarks.dat.bz2
fi

cd ../../edge

echo "✅ 설치 완료!"
echo ""
echo "실행 방법:"
echo "  source venv/bin/activate"
echo "  python3 app.py"
echo ""
echo "⚠️ 웹캠 권한을 시스템 환경설정에서 부여해야 합니다."
```

사용 방법:
```bash
cd /Users/tommykong/Downloads/GazeTracking-master\ 4/edge
chmod +x mac-setup.sh
./mac-setup.sh
```

---

## 🎉 결론

### 맥에서 작동하지 않는 주요 원인:
1. **WebSocket 라이브러리 부재** ← 가장 중요!
2. Python 의존성 부족
3. 웹캠 권한 미부여

### 해결 후 기대 효과:
✅ 시선 포인터 실시간 표시
✅ 눈 깜빡임 클릭 작동
✅ Dwell-time 진행도 표시
✅ 라즈베리파이와 동일하게 작동

### 라즈베리파이에서는:
라즈베리파이에서는 `requirements.txt` 설치만으로도 모든 의존성이 자동으로 설치되므로 **별도의 추가 설정 없이 바로 작동**합니다!
