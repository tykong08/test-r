#!/bin/bash
# GazeHome Edge Device - 라즈베리파이 실행 스크립트
# ====================================================
# 라즈베리파이에서 Docker Compose를 사용하여 시스템을 실행합니다.

set -e  # 오류 발생 시 스크립트 중단

echo "============================================"
echo " GazeHome Edge Device - 라즈베리파이 실행"
echo "============================================"

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "설치 방법: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

# Docker Compose 설치 확인
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "설치 방법: sudo apt-get install docker-compose"
    exit 1
fi

# 카메라 디바이스 확인
if [ ! -c /dev/video0 ]; then
    echo "⚠️  경고: /dev/video0 카메라를 찾을 수 없습니다."
    echo "카메라가 연결되어 있는지 확인하세요."
fi

# config.json 확인
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json이 없습니다. 기본 설정 파일을 생성합니다..."
    cat > config.json <<EOF
{
    "user_uuid": "$(uuidgen)",
    "ai_service_url": "http://localhost:8001",
    "mock_mode": true,
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
EOF
    echo "✅ config.json 생성 완료"
fi

# 로그 디렉토리 생성
mkdir -p logs

# 이미지 빌드 (처음 실행 시 또는 업데이트 시)
echo ""
echo "📦 Docker 이미지 빌드 중..."
echo "⏱️  ARM 환경에서 첫 빌드는 10-15분 정도 소요될 수 있습니다."
docker-compose build

# 컨테이너 실행
echo ""
echo "🚀 컨테이너 시작 중..."
docker-compose up -d

# 상태 확인
echo ""
echo "📊 컨테이너 상태:"
docker-compose ps

# 로그 tail
echo ""
echo "📝 실시간 로그 (Ctrl+C로 종료):"
echo "전체 로그 보기: docker-compose logs -f"
echo ""
sleep 2
docker-compose logs --tail=20 -f

# 사용법 안내
cat <<EOF

============================================
 GazeHome Edge Device 실행 완료!
============================================

🌐 웹 UI 접속:
   http://localhost:8000
   또는
   http://$(hostname -I | awk '{print $1}'):8000

📊 유용한 명령어:
   상태 확인:    docker-compose ps
   로그 보기:    docker-compose logs -f
   중지:        docker-compose stop
   재시작:      docker-compose restart
   완전 삭제:    docker-compose down

🔧 문제 해결:
   1. 카메라가 인식 안 될 때:
      ls -l /dev/video*
      sudo usermod -aG video $USER
   
   2. 권한 오류 발생 시:
      sudo chmod 666 /dev/video0
   
   3. 컨테이너 재빌드:
      docker-compose down
      docker-compose build --no-cache
      docker-compose up -d

============================================
EOF
