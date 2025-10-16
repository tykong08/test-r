"""
Gaze Tracker with Dwell-time Click Detection
Integrates with existing gaze_tracking module and applies calibration
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
    """Area of Interest for device mapping"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 device_id: str, action: str = "toggle"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.device_id = device_id
        self.action = action
    
    def contains(self, x: int, y: int) -> bool:
        """Check if point is inside this AOI"""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'device_id': self.device_id,
            'action': self.action
        }


class DwellClickDetector:
    """Detects clicks based on dwell time (fixation duration)"""
    
    def __init__(self, dwell_time: float = 0.8, tolerance: int = 30):
        self.dwell_time = dwell_time  # seconds
        self.tolerance = tolerance     # pixels
        
        self.fixation_start_time: Optional[float] = None
        self.fixation_position: Optional[Tuple[int, int]] = None
        self.is_dwelling = False
    
    def update(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """
        Update with new gaze position
        
        Args:
            x: Screen x coordinate
            y: Screen y coordinate
            
        Returns:
            Click position (x, y) if dwell time exceeded, None otherwise
        """
        current_time = time.time()
        
        # Check if this is a new fixation or continuation
        if self.fixation_position is None:
            # Start new fixation
            self.fixation_position = (x, y)
            self.fixation_start_time = current_time
            self.is_dwelling = True
            return None
        
        # Check if still within tolerance of fixation point
        dx = abs(x - self.fixation_position[0])
        dy = abs(y - self.fixation_position[1])
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > self.tolerance:
            # Moved away, reset fixation
            self.fixation_position = (x, y)
            self.fixation_start_time = current_time
            self.is_dwelling = True
            return None
        
        # Still fixating, check if dwell time exceeded
        elapsed = current_time - self.fixation_start_time
        
        if elapsed >= self.dwell_time:
            # Click detected!
            click_pos = self.fixation_position
            self.reset()
            return click_pos
        
        return None
    
    def reset(self):
        """Reset fixation state"""
        self.fixation_start_time = None
        self.fixation_position = None
        self.is_dwelling = False
    
    def get_progress(self) -> float:
        """Get dwell progress (0.0 - 1.0)"""
        if not self.is_dwelling or self.fixation_start_time is None:
            return 0.0
        
        elapsed = time.time() - self.fixation_start_time
        return min(elapsed / self.dwell_time, 1.0)


class BlinkClickDetector:
    """Detects clicks based on intentional blinks"""
    
    def __init__(self, blink_duration_min: float = 0.3, blink_duration_max: float = 1.0):
        self.blink_duration_min = blink_duration_min  # Minimum blink duration for click (seconds)
        self.blink_duration_max = blink_duration_max  # Maximum blink duration for click (seconds)
        
        self.blink_start_time: Optional[float] = None
        self.is_blinking = False
        self.last_gaze_position: Optional[Tuple[int, int]] = None
    
    def update(self, is_blinking: bool, gaze_position: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        Update with blink state
        
        Args:
            is_blinking: Whether user is currently blinking
            gaze_position: Current gaze position (for click location)
            
        Returns:
            Click position (x, y) if intentional blink detected, None otherwise
        """
        current_time = time.time()
        
        # Store gaze position when not blinking
        if not is_blinking and gaze_position:
            self.last_gaze_position = gaze_position
        
        # Blink just started
        if is_blinking and not self.is_blinking:
            self.blink_start_time = current_time
            self.is_blinking = True
            return None
        
        # Blink just ended
        if not is_blinking and self.is_blinking:
            self.is_blinking = False
            
            if self.blink_start_time is not None:
                blink_duration = current_time - self.blink_start_time
                
                # Check if blink duration is in valid range
                if self.blink_duration_min <= blink_duration <= self.blink_duration_max:
                    # Intentional blink detected!
                    logger.info(f"Blink click detected: {blink_duration:.2f}s")
                    return self.last_gaze_position
                
            self.blink_start_time = None
        
        return None
    
    def reset(self):
        """Reset blink state"""
        self.blink_start_time = None
        self.is_blinking = False


class GazeTracker:
    """
    Main gaze tracker with calibration and click detection
    """
    
    def __init__(self, screen_width: int, screen_height: int, 
                 dwell_time: float = 0.8, camera_index: int = 0, 
                 click_mode: str = 'dwell'):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize gaze tracking
        self.gaze = GazeTracking()
        
        # Initialize calibrator
        self.calibrator = GazeCalibrator(screen_width, screen_height)
        
        # Initialize click detectors
        self.dwell_detector = DwellClickDetector(dwell_time)
        self.blink_detector = BlinkClickDetector()
        
        # Click mode: 'dwell', 'blink', or 'both'
        self.click_mode = click_mode
        
        # For backward compatibility
        self.click_detector = self.dwell_detector
        
        # AOI mapping for devices
        self.aois: List[AOI] = []
        
        # Click callback
        self.click_callback: Optional[Callable] = None
        
        # Camera
        self.camera_index = camera_index
        
        logger.info(f"GazeTracker initialized: {screen_width}x{screen_height}")
    
    def add_aoi(self, x: int, y: int, width: int, height: int, 
                device_id: str, action: str = "toggle"):
        """Add an Area of Interest for device mapping"""
        aoi = AOI(x, y, width, height, device_id, action)
        self.aois.append(aoi)
        logger.info(f"Added AOI for {device_id}: ({x}, {y}, {width}, {height})")
    
    def clear_aois(self):
        """Clear all AOIs"""
        self.aois.clear()
        logger.info("Cleared all AOIs")
    
    def set_click_callback(self, callback: Callable):
        """Set callback function for click events"""
        self.click_callback = callback
    
    def get_raw_gaze_ratio(self) -> Optional[Tuple[float, float]]:
        """
        Get raw gaze ratios from gaze tracking
        
        Returns:
            (horizontal_ratio, vertical_ratio) or None if not available
        """
        h_ratio = self.gaze.horizontal_ratio()
        v_ratio = self.gaze.vertical_ratio()
        
        if h_ratio is None or v_ratio is None:
            return None
        
        return (h_ratio, v_ratio)
    
    def get_calibrated_gaze_position(self) -> Optional[Tuple[int, int]]:
        """
        Get calibrated gaze position in screen coordinates
        
        Returns:
            (screen_x, screen_y) or None if not available
        """
        raw_ratios = self.get_raw_gaze_ratio()
        if raw_ratios is None:
            return None
        
        h_ratio, v_ratio = raw_ratios
        
        # Apply calibration if available
        if self.calibrator.is_calibrated:
            h_ratio, v_ratio = self.calibrator.apply_calibration(h_ratio, v_ratio)
        
        # Convert to screen coordinates
        screen_x = int(h_ratio * self.screen_width)
        screen_y = int(v_ratio * self.screen_height)
        
        # Clamp to screen bounds
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        return (screen_x, screen_y)
    
    def update(self, frame):
        """
        Update gaze tracking with new frame
        
        Args:
            frame: Camera frame (numpy array)
            
        Returns:
            Dictionary with gaze information and any detected clicks
        """
        # Refresh gaze tracking
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
            # No valid gaze, reset click detectors
            self.dwell_detector.reset()
            self.blink_detector.reset()
        
        return result
    
    def get_annotated_frame(self):
        """Get frame with gaze annotations"""
        return self.gaze.annotated_frame()
    
    def is_blinking(self) -> bool:
        """Check if user is blinking"""
        return self.gaze.is_blinking()
    
    def load_calibration(self, filepath) -> bool:
        """Load calibration from file"""
        return self.calibrator.load_calibration(filepath)
    
    def save_calibration(self, filepath):
        """Save calibration to file"""
        self.calibrator.save_calibration(filepath)
    
    def start_calibration(self):
        """Start calibration process"""
        self.calibrator.reset()
        logger.info("Started calibration")
    
    def add_calibration_sample(self):
        """Add calibration sample for current target"""
        raw_ratios = self.get_raw_gaze_ratio()
        if raw_ratios is None:
            return False
        
        return self.calibrator.add_sample(raw_ratios[0], raw_ratios[1])
    
    def next_calibration_target(self) -> bool:
        """Move to next calibration target"""
        return self.calibrator.move_to_next_target()
    
    def get_calibration_progress(self) -> Dict:
        """Get calibration progress"""
        return self.calibrator.get_progress()
    
    def is_calibrated(self) -> bool:
        """Check if calibration is complete"""
        return self.calibrator.is_calibrated
