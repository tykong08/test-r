"""
GazeHome - 설정 관리 모듈
==========================
config.json 파일을 로드하고 관리하는 모듈입니다.

주요 기능:
- JSON 기반 설정 파일 읽기/쓰기
- 설정값 검증 및 기본값 제공
- Property를 통한 타입 안전한 접근

설정 항목:
- user_uuid: 사용자 고유 식별자
- ai_service_url: AI 서비스 엔드포인트
- mock_mode: 테스트 모드 활성화 여부
- gaze: 시선 추적 관련 설정 (dwell_time, screen_size 등)
- polling: 폴링 간격 설정

사용 예:
    from core.config import config
    print(config.dwell_time)  # 0.8
    config.save_config()

작성자: GazeHome Team
"""
import json
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """설정 관리 클래스"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(__file__).parent.parent / config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """JSON 파일에서 설정 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def save_config(self):
        """설정을 JSON 파일에 저장"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    @property
    def user_uuid(self) -> str:
        """사용자 UUID 가져오기"""
        return self.config.get("user_uuid", "")
    
    @property
    def ai_service_url(self) -> str:
        """AI 서비스 URL 가져오기"""
        return self.config.get("ai_service_url", "http://localhost:8001")
    
    @property
    def dwell_time(self) -> float:
        """시선 클릭을 위한 응시 시간 가져오기"""
        return self.config.get("gaze", {}).get("dwell_time", 0.8)
    
    @property
    def screen_width(self) -> int:
        """화면 너비 가져오기"""
        return self.config.get("gaze", {}).get("screen_width", 1920)
    
    @property
    def screen_height(self) -> int:
        """화면 높이 가져오기"""
        return self.config.get("gaze", {}).get("screen_height", 1080)
    
    @property
    def camera_index(self) -> int:
        """카메라 인덱스 가져오기"""
        return self.config.get("gaze", {}).get("camera_index", 0)
    
    @property
    def calibration_file(self) -> Path:
        """캘리브레이션 파일 경로 가져오기"""
        filename = self.config.get("calibration_file", "calibration_params.json")
        return Path(__file__).parent.parent / filename
    
    @property
    def device_status_interval(self) -> float:
        """디바이스 상태 폴링 간격 가져오기"""
        return self.config.get("polling", {}).get("device_status_interval", 5.0)
    
    @property
    def recommendation_interval(self) -> float:
        """추천 폴링 간격 가져오기"""
        return self.config.get("polling", {}).get("recommendation_interval", 3.0)
    
    @property
    def mock_mode(self) -> bool:
        """Mock 모드 설정 가져오기"""
        return self.config.get("mock_mode", False)
    
    @property
    def config_data(self) -> Dict[str, Any]:
        """원시 설정 데이터 가져오기"""
        return self.config


# 전역 설정 인스턴스
config = Config()
