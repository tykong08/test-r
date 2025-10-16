# GazeHome Edge Device - Dockerfile
# 라즈베리파이 (ARM 아키텍처) 지원
# =====================================

# Python 3.11 기반 이미지 (ARM64 지원)
FROM python:3.11-slim-bullseye

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 라이브러리 설치
RUN apt-get update && apt-get install -y \
    # OpenCV 의존성
    libopencv-dev \
    python3-opencv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    # dlib 빌드 의존성
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    # 카메라 관련
    v4l-utils \
    # 기타 유틸리티
    wget \
    && rm -rf /var/lib/apt/lists/*

# dlib shape predictor 모델 다운로드 (사전 다운로드)
RUN mkdir -p /app/edge/model/trained_models && \
    wget -O /app/edge/model/trained_models/shape_predictor_68_face_landmarks.dat.bz2 \
    http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 && \
    bunzip2 /app/edge/model/trained_models/shape_predictor_68_face_landmarks.dat.bz2

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
# ARM 환경에서 dlib 빌드 시간이 오래 걸릴 수 있음 (5-10분)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY edge/ /app/edge/

# 작업 디렉토리를 edge로 변경
WORKDIR /app/edge

# 설정 파일 확인
RUN if [ ! -f "config.json" ]; then \
        echo "{\"user_uuid\": \"default-uuid\", \"mock_mode\": true}" > config.json; \
    fi

# 포트 노출
EXPOSE 8000

# 카메라 권한 설정을 위한 환경 변수
ENV PYTHONUNBUFFERED=1
ENV OPENCV_VIDEOIO_DEBUG=1

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/state')"

# 애플리케이션 실행
CMD ["python", "app.py"]
