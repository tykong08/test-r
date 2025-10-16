"""
Configuration Manager for Edge Device
Handles loading and saving configuration parameters
"""
import json
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(__file__).parent.parent / config_path
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    @property
    def user_uuid(self) -> str:
        """Get user UUID"""
        return self.config.get("user_uuid", "")
    
    @property
    def ai_service_url(self) -> str:
        """Get AI service URL"""
        return self.config.get("ai_service_url", "http://localhost:8001")
    
    @property
    def dwell_time(self) -> float:
        """Get dwell time for gaze click"""
        return self.config.get("gaze", {}).get("dwell_time", 0.8)
    
    @property
    def screen_width(self) -> int:
        """Get screen width"""
        return self.config.get("gaze", {}).get("screen_width", 1920)
    
    @property
    def screen_height(self) -> int:
        """Get screen height"""
        return self.config.get("gaze", {}).get("screen_height", 1080)
    
    @property
    def camera_index(self) -> int:
        """Get camera index"""
        return self.config.get("gaze", {}).get("camera_index", 0)
    
    @property
    def calibration_file(self) -> Path:
        """Get calibration file path"""
        filename = self.config.get("calibration_file", "calibration_params.json")
        return Path(__file__).parent.parent / filename
    
    @property
    def device_status_interval(self) -> float:
        """Get device status polling interval"""
        return self.config.get("polling", {}).get("device_status_interval", 5.0)
    
    @property
    def recommendation_interval(self) -> float:
        """Get recommendation polling interval"""
        return self.config.get("polling", {}).get("recommendation_interval", 3.0)
    
    @property
    def mock_mode(self) -> bool:
        """Get mock mode setting"""
        return self.config.get("mock_mode", False)
    
    @property
    def config_data(self) -> Dict[str, Any]:
        """Get raw config data"""
        return self.config


# Global config instance
config = Config()
