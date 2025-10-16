"""
GazeHome - 시선 추적 및 클릭 감지 모듈
======================================
dlib 기반 시선 추적과 두 가지 클릭 방식을 통합한 핵심 모듈입니다.

주요 클래스:
- GazeTracker: 메인 시선 추적 및 클릭 관리 클래스
- DwellClickDetector: 응시(Dwell) 기반 클릭 감지
- BlinkClickDetector: 깜빡임(Blink) 기반 클릭 감지  
- AOI: 디바이스 매핑을 위한 관심 영역(Area of Interest)

클릭 모드:
- dwell: 일정 시간 이상 응시 시 클릭
- blink: 0.3~1.0초 사이의 의도적 깜빡임으로 클릭
- both: 두 방식 모두 사용 가능

시선 보정(Calibration):
- 5포인트 보정 방식 사용
- 화면 좌표계로 변환 및 정규화
- 보정 데이터 저장/로드 기능

작성자: GazeHome Team
"""
import sys
import os
import time
import logging
from typing import Optional, Tuple, Callable, Dict, List
import numpy as np

# Import from model directory
from model.gaze_tracking import GazeTracking
from .calibrator import GazeCalibrator

logger = logging.getLogger(__name__)


class AOI:
    """디바이스 매핑을 위한 관심 영역 (Area of Interest)"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 device_id: str, action: str = "toggle"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.device_id = device_id
        self.action = action
    
    def contains(self, x: int, y: int) -> bool:
        """포인트가 이 AOI 안에 있는지 확인"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'device_id': self.device_id,
            'action': self.action
        }


class DwellClickDetector:
    """응시 시간(fixation duration) 기반 클릭 감지"""
    
    def __init__(self, dwell_time: float = 0.8, tolerance: int = 30):
        self.dwell_time = dwell_time  # 초 단위
        self.tolerance = tolerance     # 픽셀
        
        self.fixation_start_time: Optional[float] = None
        self.fixation_position: Optional[Tuple[int, int]] = None
        self.is_dwelling = False
    
    def update(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """
        새로운 시선 위치로 업데이트
        
        Args:
            x: 화면 x 좌표
            y: 화면 y 좌표
            
        Returns:
            응시 시간 초과 시 클릭 위치 (x, y), 그렇지 않으면 None
        """
        current_time = time.time()
        
        # 새로운 응시 시작인지 지속인지 확인
        if self.fixation_position is None:
            # 새로운 응시 시작
            self.fixation_position = (x, y)
            self.fixation_start_time = current_time
            self.is_dwelling = True
            return None
        
        # 응시 지점의 허용 범위 내에 있는지 확인
        dx = abs(x - self.fixation_position[0])
        dy = abs(y - self.fixation_position[1])
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > self.tolerance:
            # 이동했으므로 응시 초기화
            self.fixation_position = (x, y)
            self.fixation_start_time = current_time
            self.is_dwelling = True
            return None
        
        # 여전히 응시 중, 응시 시간 초과 여부 확인
        elapsed = current_time - self.fixation_start_time
        
        if elapsed >= self.dwell_time:
            # 클릭 감지!
            click_pos = self.fixation_position
            self.reset()
            return click_pos
        
        return None
    
    def reset(self):
        """응시 상태 초기화"""
        self.fixation_start_time = None
        self.fixation_position = None
        self.is_dwelling = False
    
    def get_progress(self) -> float:
        """응시 진행률 가져오기 (0.0 - 1.0)"""
        if not self.is_dwelling or self.fixation_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.fixation_start_time
        return min(elapsed / self.dwell_time, 1.0)


class BlinkClickDetector:
    """의도적인 깜빡임 기반 클릭 감지"""
    
    def __init__(self, blink_duration_min: float = 0.3, blink_duration_max: float = 1.0):
        self.blink_duration_min = blink_duration_min  # 클릭으로 인정되는 최소 깜빡임 시간 (초)
        self.blink_duration_max = blink_duration_max  # 클릭으로 인정되는 최대 깜빡임 시간 (초)
        
        self.blink_start_time: Optional[float] = None
        self.is_blinking = False
        self.last_gaze_position: Optional[Tuple[int, int]] = None
    
    def update(self, is_blinking: bool, gaze_position: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        깜빡임 상태로 업데이트
        
        Args:
            is_blinking: 현재 사용자가 깜빡이고 있는지 여부
            gaze_position: 현재 시선 위치 (클릭 위치용)
            
        Returns:
            의도적인 깜빡임 감지 시 클릭 위치 (x, y), 그렇지 않으면 None
        """
        current_time = time.time()
        
        # 깜빡이지 않을 때 시선 위치 저장
        if not is_blinking and gaze_position:
            self.last_gaze_position = gaze_position
        
        # 깜빡임 시작
        if is_blinking and not self.is_blinking:
            self.blink_start_time = current_time
            self.is_blinking = True
            return None
        
        # 깜빡임 종료
        if not is_blinking and self.is_blinking:
            self.is_blinking = False
            
            if self.blink_start_time is not None:
                blink_duration = current_time - self.blink_start_time
                
                # 깜빡임 지속 시간이 유효한 범위인지 확인
                if self.blink_duration_min <= blink_duration <= self.blink_duration_max:
                    # 의도적인 깜빡임 감지!
                    logger.info(f"Blink click detected: {blink_duration:.2f}s")
                    return self.last_gaze_position
                
            self.blink_start_time = None
        
        return None
    
    def reset(self):
        """깜빡임 상태 초기화"""
        self.blink_start_time = None
        self.is_blinking = False


class GazeTracker:
    """
    캘리브레이션 및 클릭 감지 기능을 포함한 메인 시선 추적기
    """
    
    def __init__(self, screen_width: int, screen_height: int, 
                 dwell_time: float = 0.8, camera_index: int = 0, 
                 click_mode: str = 'dwell'):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 시선 추적 초기화
        self.gaze = GazeTracking()
        
        # 캘리브레이터 초기화
        self.calibrator = GazeCalibrator(screen_width, screen_height)
        
        # 클릭 감지기 초기화
        self.dwell_detector = DwellClickDetector(dwell_time)
        self.blink_detector = BlinkClickDetector()
        
        # 클릭 모드: 'dwell', 'blink', 또는 'both'
        self.click_mode = click_mode
        
        # 하위 호환성 유지
        self.click_detector = self.dwell_detector
        
        # 디바이스를 위한 AOI 매핑
        self.aois: List[AOI] = []
        
        # 클릭 콜백
        self.click_callback: Optional[Callable] = None
        
        # 카메라
        self.camera_index = camera_index
        
        logger.info(f"GazeTracker initialized: {screen_width}x{screen_height}")
    
    def add_aoi(self, x: int, y: int, width: int, height: int, 
                device_id: str, action: str = "toggle"):
        """디바이스 매핑을 위한 관심 영역 추가"""
        aoi = AOI(x, y, width, height, device_id, action)
        self.aois.append(aoi)
        logger.info(f"Added AOI for {device_id}: ({x}, {y}, {width}, {height})")
    
    def clear_aois(self):
        """모든 AOI 삭제"""
        self.aois.clear()
        logger.info("Cleared all AOIs")
    
    def set_click_callback(self, callback: Callable):
        """클릭 이벤트를 위한 콜백 함수 설정"""
        self.click_callback = callback
    
    def get_raw_gaze_ratio(self) -> Optional[Tuple[float, float]]:
        """
        시선 추적에서 원시 시선 비율 가져오기
        
        Returns:
            (horizontal_ratio, vertical_ratio) 또는 사용 불가 시 None
        """
        h_ratio = self.gaze.horizontal_ratio()
        v_ratio = self.gaze.vertical_ratio()
        
        if h_ratio is None or v_ratio is None:
            return None
        
        return (h_ratio, v_ratio)
    
    def get_calibrated_gaze_position(self) -> Optional[Tuple[int, int]]:
        """
        화면 좌표에서 보정된 시선 위치 가져오기
        
        Returns:
            (screen_x, screen_y) 또는 사용 불가 시 None
        """
        raw_ratios = self.get_raw_gaze_ratio()
        if raw_ratios is None:
            return None
        
        h_ratio, v_ratio = raw_ratios
        
        # 캘리브레이션 사용 가능 시 적용
        if self.calibrator.is_calibrated:
            h_ratio, v_ratio = self.calibrator.apply_calibration(h_ratio, v_ratio)
        
        # 화면 좌표로 변환
        screen_x = int(h_ratio * self.screen_width)
        screen_y = int(v_ratio * self.screen_height)
        
        # 화면 경계로 제한
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        return (screen_x, screen_y)
    
    def update(self, frame):
        """
        새 프레임으로 시선 추적 업데이트
        
        Args:
            frame: 카메라 프레임 (numpy 배열)
            
        Returns:
            시선 정보 및 감지된 클릭이 포함된 딕셔너리
        """
        # 시선 추적 갱신
        self.gaze.refresh(frame)
        
        result = {
            'gaze_position': None,
            'raw_ratios': None,
            'click_detected': False,
            'clicked_device': None,
            'dwell_progress': 0.0,
            'pupils_detected': self.gaze.pupils_located,
            'click_method': None
        }
        
        # Get gaze position
        gaze_pos = self.get_calibrated_gaze_position()
        raw_ratios = self.get_raw_gaze_ratio()
        is_blinking = self.gaze.is_blinking()
        
        click_pos = None
        click_method = None
        
        if gaze_pos:
            result['gaze_position'] = gaze_pos
            result['raw_ratios'] = raw_ratios
            
            # Check for clicks based on mode
            if self.click_mode in ['dwell', 'both']:
                dwell_click = self.dwell_detector.update(gaze_pos[0], gaze_pos[1])
                result['dwell_progress'] = self.dwell_detector.get_progress()
                
                if dwell_click:
                    click_pos = dwell_click
                    click_method = 'dwell'
            
            if self.click_mode in ['blink', 'both']:
                blink_click = self.blink_detector.update(is_blinking, gaze_pos)
                
                if blink_click:
                    click_pos = blink_click
                    click_method = 'blink'
            
            if click_pos:
                # Click detected!
                result['click_detected'] = True
                result['click_method'] = click_method
                
                # Check if click is in any AOI
                for aoi in self.aois:
                    if aoi.contains(click_pos[0], click_pos[1]):
                        result['clicked_device'] = {
                            'device_id': aoi.device_id,
                            'action': aoi.action,
                            'position': click_pos,
                            'method': click_method
                        }
                        
                        # Call callback if set
                        if self.click_callback:
                            self.click_callback(aoi.device_id, aoi.action, click_pos)
                        
                        logger.info(f"Click detected ({click_method}): {aoi.device_id} at {click_pos}")
                        break
        else:
            # 유효한 시선이 없으면 클릭 감지기 초기화
            self.dwell_detector.reset()
            self.blink_detector.reset()
        
        return result
    
    def get_annotated_frame(self):
        """시선 주석이 추가된 프레임 가져오기"""
        return self.gaze.annotated_frame()
    
    def is_blinking(self) -> bool:
        """사용자가 깜빡이고 있는지 확인"""
        return self.gaze.is_blinking()
    
    def load_calibration(self, filepath) -> bool:
        """파일에서 캘리브레이션 로드"""
        return self.calibrator.load_calibration(filepath)
    
    def save_calibration(self, filepath):
        """파일에 캘리브레이션 저장"""
        self.calibrator.save_calibration(filepath)
    
    def start_calibration(self):
        """캘리브레이션 프로세스 시작"""
        self.calibrator.reset()
        logger.info("Started calibration")
    
    def add_calibration_sample(self):
        """현재 타겟에 대한 캘리브레이션 샘플 추가"""
        raw_ratios = self.get_raw_gaze_ratio()
        if raw_ratios is None:
            return False
        
        return self.calibrator.add_sample(raw_ratios[0], raw_ratios[1])
    
    def next_calibration_target(self) -> bool:
        """다음 캘리브레이션 타겟으로 이동"""
        return self.calibrator.move_to_next_target()
    
    def get_calibration_progress(self) -> Dict:
        """캘리브레이션 진행 상태 가져오기"""
        return self.calibrator.get_progress()
    
    def is_calibrated(self) -> bool:
        """캘리브레이션 완료 여부 확인"""
        return self.calibrator.is_calibrated
