#!/usr/bin/env python3
"""
서버 실행 스크립트 - 환경 체크 및 FastAPI 서버 시작
"""
import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """의존성 패키지 설치 여부 확인"""
    try:
        import cv2
        import numpy
        import fastapi
        import aiohttp
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False


def check_dlib_model():
    """dlib 모델 존재 여부 확인"""
    model_path = Path(__file__).parent / "model/trained_models/shape_predictor_68_face_landmarks.dat"
    if model_path.exists():
        print(f"✅ dlib model found")
        return True
    else:
        print(f"⚠️  dlib model not found: {model_path}")
        print("   Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        return False


def check_config():
    """config 파일 존재 여부 확인"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        print(f"✅ Configuration found: {config_path}")
        return True
    else:
        print(f"❌ Configuration not found: {config_path}")
        return False


def check_camera():
    """카메라 사용 가능 여부 확인"""
    try:
        import cv2
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            cam.release()
            print("✅ Camera available")
            return True
        else:
            print("⚠️  Camera not available (will try to open anyway)")
            return True  # 실패하지 않음, 나중에 작동할 수 있음
    except Exception as e:
        print(f"⚠️  Camera check failed: {e}")
        return True  # 실패하지 않음


def run_app():
    """애플리케이션 실행"""
    print("\n" + "="*60)
    print("Starting GazeHome Edge Device...")
    print("="*60 + "\n")
    
    # edge 디렉토리로 변경
    os.chdir(Path(__file__).parent)
    
    # uvicorn으로 실행
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")


def main():
    print("\n🏠 GazeHome Edge Device - Pre-flight Check")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("dlib Model", check_dlib_model),
        ("Configuration", check_config),
        ("Camera", check_camera),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    
    if not all(results):
        print("\n⚠️  Some checks failed. Proceed? (y/n): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("\n👋 Setup incomplete. Fix issues and try again.")
            return 1
    
    print("\n✅ All checks passed (or ignored)!")
    print("\nStarting server...")
    print("\nOnce running, open browser to:")
    print("  → http://localhost:8000")
    print("\nMake sure these are running (if not using mock mode):")
    print("  → AI Service: http://localhost:8001")
    print("\nPress Ctrl+C to stop")
    print("="*60)
    
    run_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
