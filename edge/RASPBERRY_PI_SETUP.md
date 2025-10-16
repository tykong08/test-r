# 🍓 Raspberry Pi 설치 가이드

GazeHome Edge Device를 Raspberry Pi에서 실행하기 위한 완전한 설정 가이드입니다.

## 📋 목차
1. [하드웨어 요구사항](#하드웨어-요구사항)
2. [라즈베리파이 OS 설정](#라즈베리파이-os-설정)
3. [Python 환경 설정](#python-환경-설정)
4. [의존성 패키지 설치](#의존성-패키지-설치)
5. [Edge Device 설치](#edge-device-설치)
6. [문제 해결](#문제-해결)
7. [성능 최적화](#성능-최적화)

---

## 하드웨어 요구사항

### 최소 사양
- **Raspberry Pi 4 Model B** (권장: 4GB RAM 이상)
- **USB 웹캠** 또는 Raspberry Pi Camera Module
- **16GB 이상 microSD 카드**
- **안정적인 전원 공급** (5V 3A)

### 권장 사양
- **Raspberry Pi 4 Model B 8GB RAM**
- **Raspberry Pi Camera Module v2** (더 나은 성능)
- **32GB 이상 microSD 카드** (Class 10)
- **공식 Raspberry Pi 전원 어댑터**

### 호환성
| 모델              | 지원 | 성능 | 비고          |
| ----------------- | ---- | ---- | ------------- |
| Raspberry Pi 4    | ✅    | 우수 | 권장          |
| Raspberry Pi 3 B+ | ✅    | 보통 | 느릴 수 있음  |
| Raspberry Pi 3 B  | ⚠️    | 느림 | 기본 테스트만 |
| Raspberry Pi Zero | ❌    | 불가 | CPU 부족      |

---

## 라즈베리파이 OS 설정

### 1. OS 설치

**Raspberry Pi OS (64-bit) Lite 권장**

```bash
# Raspberry Pi Imager 사용
# https://www.raspberrypi.com/software/

# 또는 직접 다운로드
# https://www.raspberrypi.com/software/operating-systems/
```

**선택사항:**
- ✅ **Lite (권장)** - 헤드리스 서버용, 리소스 절약
- ⚠️ **Desktop** - GUI 필요시, 더 많은 RAM 사용

### 2. 초기 설정

```bash
# SSH 활성화 (Raspberry Pi Imager에서 설정 가능)
# 또는 boot 파티션에 빈 'ssh' 파일 생성

# WiFi 설정 (선택사항)
sudo raspi-config
# Network Options → Wi-Fi

# 시스템 업데이트
sudo apt update
sudo apt upgrade -y
```

### 3. 카메라 활성화

#### USB 웹캠 사용시
```bash
# 자동으로 인식됨
# /dev/video0 확인
ls -l /dev/video*
```

#### Raspberry Pi Camera Module 사용시
```bash
# 카메라 활성화
sudo raspi-config
# Interface Options → Camera → Enable

# 재부팅
sudo reboot

# 테스트
raspistill -o test.jpg
```

---

## Python 환경 설정

### 1. Python 3.11 설치

Raspberry Pi OS는 기본적으로 Python 3.9가 설치되어 있습니다. Python 3.11을 설치합니다:

```bash
# 빌드 도구 설치
sudo apt install -y build-essential tk-dev libncurses5-dev \
  libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev \
  libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev \
  zlib1g-dev libffi-dev

# Python 3.11 소스 다운로드
cd ~
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tar -xf Python-3.11.0.tgz
cd Python-3.11.0

# 컴파일 및 설치 (약 30-60분 소요)
./configure --enable-optimizations
make -j4
sudo make altinstall

# 확인
python3.11 --version
```

**또는 기본 Python 3.9 사용:**
```bash
# Python 3.9로도 작동 가능
python3 --version
```

### 2. 가상환경 생성

```bash
# venv 생성
python3.11 -m venv ~/gaze_env

# 활성화
source ~/gaze_env/bin/activate

# pip 업그레이드
pip install --upgrade pip setuptools wheel
```

---

## 의존성 패키지 설치

### 1. 시스템 패키지 설치

```bash
# OpenCV 의존성
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libjasper-dev libqtgui4 libqt4-test

# dlib 의존성 (중요!)
sudo apt install -y cmake
sudo apt install -y libboost-all-dev

# 카메라 관련
sudo apt install -y libv4l-dev v4l-utils
```

### 2. Python 패키지 설치

#### 방법 1: 수정된 requirements.txt 사용 (권장)

**`requirements-rpi.txt` 생성:**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
opencv-python==4.8.1.78
numpy==1.24.3
aiohttp==3.9.1
# dlib은 별도 설치 필요
scipy==1.11.4
python-multipart==0.0.6
jinja2==3.1.2
```

```bash
# 설치
pip install -r requirements-rpi.txt
```

#### 방법 2: dlib 직접 빌드

**⚠️ 주의: 시간이 오래 걸립니다 (1-2시간)**

```bash
# dlib 소스 클론
cd ~
git clone https://github.com/davisking/dlib.git
cd dlib

# 빌드 및 설치
mkdir build
cd build
cmake ..
cmake --build . --config Release

# Python 바인딩 설치
cd ..
python3.11 setup.py install

# 또는 pip로 설치 (자동 빌드, 시간 오래 걸림)
pip install dlib
```

#### 방법 3: 미리 빌드된 wheel 사용 (가장 빠름)

```bash
# piwheels 사용 (Raspberry Pi OS 전용)
pip install dlib --extra-index-url https://www.piwheels.org/simple
```

### 3. OpenCV 설치

```bash
# 시스템 OpenCV 사용 (권장)
sudo apt install -y python3-opencv

# 또는 pip로 설치 (느림)
pip install opencv-python==4.8.1.78
```

---

## Edge Device 설치

### 1. 파일 전송

**방법 A: Git 사용**
```bash
cd ~
git clone <your-repository-url>
cd GazeTracking-master/edge
```

**방법 B: SCP 사용**
```bash
# 로컬 머신에서 실행
scp -r ./edge pi@<raspberry-pi-ip>:~/
```

**방법 C: USB 드라이브**
```bash
# USB에서 복사
cp -r /media/usb/edge ~/
```

### 2. 설정 파일 수정

```bash
cd ~/edge
nano config.json
```

```json
{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "ai_service_url": "http://<ai-service-ip>:8001",
  "mock_mode": false,
  "gaze": {
    "dwell_time": 0.8,
    "calibration_points": 5,
    "screen_width": 1920,
    "screen_height": 1080,
    "camera_index": 0
  },
  "polling": {
    "device_status_interval": 5.0,
    "recommendation_interval": 3.0
  },
  "calibration_file": "calibration_params.json"
}
```

**카메라 인덱스 확인:**
```bash
v4l2-ctl --list-devices
```

### 3. 테스트 실행

```bash
# Mock 모드로 테스트
python app.py

# 브라우저에서 접속
# http://<raspberry-pi-ip>:8000
```

---

## 문제 해결

### 1. dlib 설치 실패

**증상:**
```
ERROR: Could not build wheels for dlib
```

**해결:**
```bash
# swap 메모리 증가 (컴파일 중 메모리 부족 방지)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 (2GB)
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# 재시도
pip install dlib
```

### 2. 카메라를 찾을 수 없음

**증상:**
```
WARNING - Could not open camera
```

**해결:**
```bash
# 카메라 장치 확인
ls -l /dev/video*

# 권한 확인
sudo usermod -a -G video $USER

# 로그아웃 후 재로그인 필요
```

### 3. OpenCV import 오류

**증상:**
```
ImportError: libIlmImf.so.22: cannot open shared object file
```

**해결:**
```bash
sudo apt install -y libopenexr-dev
```

### 4. 성능이 너무 느림

**증상:**
- FPS < 10
- 응답 지연

**해결:**
```bash
# GPU 메모리 증가
sudo raspi-config
# Performance Options → GPU Memory → 256

# CPU governor 변경
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### 5. 메모리 부족

**증상:**
```
MemoryError
```

**해결:**
```bash
# 불필요한 서비스 중지
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# swap 증가 (위 참고)
```

---

## 성능 최적화

### 1. 해상도 조정

`config.json`:
```json
{
  "gaze": {
    "screen_width": 1280,
    "screen_height": 720
  }
}
```

### 2. CPU 오버클럭 (선택사항)

```bash
sudo nano /boot/config.txt
```

```ini
# Raspberry Pi 4
over_voltage=6
arm_freq=2000

# 냉각팬 필수!
```

### 3. 경량화 옵션

**Mock 모드로 UI만 테스트:**
```json
{
  "mock_mode": true
}
```

**Polling 간격 늘리기:**
```json
{
  "polling": {
    "device_status_interval": 10.0,
    "recommendation_interval": 5.0
  }
}
```

### 4. 자동 시작 설정

```bash
# systemd 서비스 생성
sudo nano /etc/systemd/system/gazehome-edge.service
```

```ini
[Unit]
Description=GazeHome Edge Device
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/edge
ExecStart=/home/pi/gaze_env/bin/python /home/pi/edge/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 활성화
sudo systemctl enable gazehome-edge.service
sudo systemctl start gazehome-edge.service

# 상태 확인
sudo systemctl status gazehome-edge.service
```

---

## 체크리스트

설치 전 체크리스트:

- [ ] Raspberry Pi 4 (4GB 이상)
- [ ] Raspberry Pi OS (64-bit) 설치
- [ ] 카메라 연결 및 테스트
- [ ] 네트워크 설정 완료
- [ ] Python 3.11 (또는 3.9) 설치
- [ ] 가상환경 생성
- [ ] 시스템 패키지 설치
- [ ] dlib 빌드 완료
- [ ] OpenCV 설치 완료
- [ ] Edge Device 코드 복사
- [ ] `config.json` 설정
- [ ] Mock 모드 테스트 성공
- [ ] 실제 모드 테스트 성공

---

## 참고 자료

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [dlib on Raspberry Pi](http://dlib.net/)
- [OpenCV on Raspberry Pi](https://docs.opencv.org/4.x/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 예상 설치 시간

| 단계               | 시간       |
| ------------------ | ---------- |
| OS 설치 및 설정    | 30분       |
| Python 3.11 빌드   | 60분       |
| 시스템 패키지 설치 | 15분       |
| dlib 빌드          | 90분       |
| Python 패키지 설치 | 30분       |
| Edge Device 설정   | 10분       |
| **총합**           | **~4시간** |

**piwheels 사용시: ~1.5시간**

---

**완료되면 브라우저에서 `http://<raspberry-pi-ip>:8000` 접속!** 🍓✨
