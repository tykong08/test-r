# 🍓 라즈베리 파이 설정 가이드

## 하드웨어 사양

### 필수 구성요소
- **라즈베리 파이 4** (2GB 이상 권장)
- **7인치 터치스크린 디스플레이** (800x480)
- **HD 웹캠** (1280x720 @ 30fps 지원)
- **microSD 카드** (32GB 이상 권장)
- **전원 어댑터** (5V 3A USB-C)

### 권장 사양
- 라즈베리 파이 4 4GB/8GB 모델
- USB 3.0 HD 웹캠 (자동 초점 기능)
- 방열판 및 쿨링 팬

---

## 소프트웨어 설치

### 1. 라즈베리 파이 OS 설치
```bash
# Raspberry Pi Imager를 사용하여 OS 설치
# 권장: Raspberry Pi OS (64-bit) with desktop
```

### 2. 시스템 업데이트
```bash
sudo apt update
sudo apt upgrade -y
```

### 3. 필수 패키지 설치
```bash
# Python 3.11 설치
sudo apt install python3.11 python3.11-venv python3-pip -y

# OpenCV 의존성
sudo apt install libopencv-dev python3-opencv -y
sudo apt install libatlas-base-dev libjasper-dev libqtgui4 libqt4-test -y

# 카메라 라이브러리
sudo apt install v4l-utils -y

# dlib 빌드 의존성
sudo apt install build-essential cmake -y
sudo apt install libx11-dev libopenblas-dev liblapack-dev -y
```

### 4. 웹캠 설정 확인
```bash
# 연결된 카메라 확인
v4l2-ctl --list-devices

# 지원 해상도 확인
v4l2-ctl --device=/dev/video0 --list-formats-ext

# 웹캠 테스트
ffplay /dev/video0
```

---

## 디스플레이 설정

### 7인치 터치스크린 설정
```bash
# /boot/config.txt 편집
sudo nano /boot/config.txt

# 다음 내용 추가/확인
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=800 480 60 6 0 0 0
display_rotate=0  # 필요시 회전 (0, 1, 2, 3)
```

### 터치스크린 캘리브레이션
```bash
sudo apt install xinput-calibrator -y
xinput_calibrator
```

---

## GazeHome 설치

### 1. 프로젝트 클론
```bash
cd ~
git clone [repository-url] GazeHome
cd GazeHome/edge
```

### 2. 가상환경 생성
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt

# dlib 수동 설치 (시간이 오래 걸림)
pip install dlib --no-cache-dir
```

### 4. 설정 파일 확인
`edge/config.json` 파일이 다음 설정을 포함하는지 확인:

```json
{
  "gaze": {
    "screen_width": 800,
    "screen_height": 480,
    "camera_index": 0,
    "camera_width": 1280,
    "camera_height": 720,
    "camera_fps": 30
  },
  "device": {
    "type": "raspberry_pi",
    "display": "7inch",
    "camera": "hd_webcam"
  }
}
```

---

## 실행

### 수동 실행
```bash
cd ~/GazeHome/edge
source venv/bin/activate
python run.py
```

### 브라우저 접속
```
http://localhost:8000
```

### 자동 시작 설정 (systemd)
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/gazehome.service
```

다음 내용 입력:
```ini
[Unit]
Description=GazeHome Edge Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/GazeHome/edge
Environment="PATH=/home/pi/GazeHome/edge/venv/bin"
ExecStart=/home/pi/GazeHome/edge/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 활성화:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gazehome
sudo systemctl start gazehome
sudo systemctl status gazehome
```

---

## 성능 최적화

### 1. GPU 메모리 증가
```bash
sudo nano /boot/config.txt

# 다음 추가
gpu_mem=256
```

### 2. 오버클로킹 (선택사항)
```bash
sudo raspi-config
# Performance Options → Overclock
```

### 3. 불필요한 서비스 비활성화
```bash
sudo systemctl disable bluetooth
sudo systemctl disable cups
```

### 4. 스왑 메모리 증가
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048

sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 문제 해결

### 카메라가 인식되지 않을 때
```bash
# 권한 확인
sudo usermod -a -G video $USER

# 재부팅
sudo reboot
```

### 성능이 느릴 때
```bash
# Python 프로세스 우선순위 증가
sudo nice -n -10 python run.py

# CPU 온도 확인
vcgencmd measure_temp
```

### 디스플레이 해상도 문제
```bash
# 현재 해상도 확인
xrandr

# 강제 해상도 설정
xrandr --output HDMI-1 --mode 800x480
```

---

## 캘리브레이션 팁

### 7인치 화면 캘리브레이션
1. **조명**: 얼굴에 충분한 조명 (정면 조명 권장)
2. **거리**: 화면으로부터 30-40cm 거리
3. **높이**: 화면이 눈높이에 오도록 조정
4. **안정**: 머리를 고정하고 눈만 움직이기
5. **샘플**: 각 포인트당 최소 30개 샘플 수집

### 웹캠 위치
- 화면 상단 중앙에 배치
- 사용자 얼굴을 정면으로 바라보도록 각도 조정
- 렌즈가 깨끗한지 확인

---

## 유지보수

### 로그 확인
```bash
# 실시간 로그
sudo journalctl -u gazehome -f

# 최근 로그
sudo journalctl -u gazehome -n 100
```

### 업데이트
```bash
cd ~/GazeHome
git pull
cd edge
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart gazehome
```

### 백업
```bash
# 캘리브레이션 데이터 백업
cp edge/calibration_params.json ~/backup/

# 전체 프로젝트 백업
tar -czf gazehome-backup.tar.gz ~/GazeHome
```

---

## 추가 리소스

- [라즈베리 파이 공식 문서](https://www.raspberrypi.org/documentation/)
- [OpenCV on Raspberry Pi](https://docs.opencv.org/master/)
- [dlib on ARM](http://dlib.net/)

---

**문제가 있으면 이슈를 등록해주세요!** 🚀
