"""
5-Point Gaze Calibration System
Implements calibration using 5 target points with affine transformation
"""
import json
import numpy as np
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GazeCalibrator:
    """
    5-point gaze calibration with affine transformation
    
    Calibration points:
    - Top-left (0.1, 0.1)
    - Top-right (0.9, 0.1)
    - Center (0.5, 0.5)
    - Bottom-left (0.1, 0.9)
    - Bottom-right (0.9, 0.9)
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 5 calibration target positions (normalized coordinates 0-1)
        self.target_positions = [
            (0.1, 0.1),   # Top-left
            (0.9, 0.1),   # Top-right
            (0.5, 0.5),   # Center
            (0.1, 0.9),   # Bottom-left
            (0.9, 0.9),   # Bottom-right
        ]
        
        # Collected samples for each target
        self.samples: Dict[int, List[Tuple[float, float]]] = {i: [] for i in range(5)}
        
        # Calibration parameters (affine transformation matrix)
        self.calibration_matrix: Optional[np.ndarray] = None
        self.translation_vector: Optional[np.ndarray] = None
        
        # Calibration state
        self.current_target_index = 0
        self.is_calibrated = False
        
        # Sample collection parameters
        self.min_samples_per_target = 30
        self.max_samples_per_target = 50
        self.stability_threshold = 0.05  # Maximum std deviation for stable samples
    
    def get_current_target_position(self) -> Tuple[int, int]:
        """Get current calibration target position in screen coordinates"""
        if self.current_target_index >= len(self.target_positions):
            return (0, 0)
        
        norm_x, norm_y = self.target_positions[self.current_target_index]
        screen_x = int(norm_x * self.screen_width)
        screen_y = int(norm_y * self.screen_height)
        return (screen_x, screen_y)
    
    def add_sample(self, gaze_x: float, gaze_y: float) -> bool:
        """
        Add a gaze sample for the current target
        
        Args:
            gaze_x: Horizontal gaze ratio (0.0 - 1.0)
            gaze_y: Vertical gaze ratio (0.0 - 1.0)
            
        Returns:
            True if enough samples collected for current target
        """
        if self.current_target_index >= len(self.target_positions):
            return False
        
        self.samples[self.current_target_index].append((gaze_x, gaze_y))
        
        # Check if we have enough samples
        if len(self.samples[self.current_target_index]) >= self.min_samples_per_target:
            return True
        
        return False
    
    def move_to_next_target(self) -> bool:
        """
        Move to next calibration target
        
        Returns:
            True if calibration is complete
        """
        self.current_target_index += 1
        
        if self.current_target_index >= len(self.target_positions):
            # All targets done, compute calibration
            self.compute_calibration()
            return True
        
        return False
    
    def _filter_stable_samples(self, samples: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Filter samples to keep only stable ones (low variance)
        Uses sliding window to find the most stable subsequence
        """
        if len(samples) < self.min_samples_per_target:
            return samples
        
        samples_array = np.array(samples)
        
        # Use the last min_samples as they're usually most stable
        # (user has had time to fixate)
        stable_samples = samples_array[-self.min_samples_per_target:]
        
        # Check if variance is acceptable
        std_x = np.std(stable_samples[:, 0])
        std_y = np.std(stable_samples[:, 1])
        
        if std_x < self.stability_threshold and std_y < self.stability_threshold:
            return stable_samples.tolist()
        else:
            # If not stable, use all samples and hope for the best
            logger.warning(f"Samples not stable (std_x={std_x:.4f}, std_y={std_y:.4f})")
            return samples
    
    def compute_calibration(self):
        """
        Compute affine transformation from collected samples
        Uses least-squares to find best-fit transformation
        """
        # Filter and average samples for each target
        gaze_points = []
        screen_points = []
        
        for i in range(len(self.target_positions)):
            if not self.samples[i]:
                logger.error(f"No samples for target {i}")
                continue
            
            # Filter stable samples
            stable = self._filter_stable_samples(self.samples[i])
            
            # Average the stable samples
            avg_gaze_x = np.mean([s[0] for s in stable])
            avg_gaze_y = np.mean([s[1] for s in stable])
            gaze_points.append([avg_gaze_x, avg_gaze_y])
            
            # Get corresponding screen point (normalized)
            screen_points.append(list(self.target_positions[i]))
            
            logger.info(f"Target {i}: {len(stable)} stable samples, avg=({avg_gaze_x:.3f}, {avg_gaze_y:.3f})")
        
        # Convert to numpy arrays
        gaze_points = np.array(gaze_points, dtype=np.float32)
        screen_points = np.array(screen_points, dtype=np.float32)
        
        # Compute affine transformation using least squares
        # screen = M * gaze + t
        # We solve: [screen_x, screen_y] = [[a, b], [c, d]] * [gaze_x, gaze_y] + [tx, ty]
        
        # Add homogeneous coordinate
        ones = np.ones((gaze_points.shape[0], 1), dtype=np.float32)
        gaze_homogeneous = np.hstack([gaze_points, ones])
        
        # Solve using least squares
        # screen = gaze_homogeneous @ transform_matrix
        transform_matrix, residuals, rank, s = np.linalg.lstsq(
            gaze_homogeneous, screen_points, rcond=None
        )
        
        # Extract matrix and translation
        self.calibration_matrix = transform_matrix[:2, :].T  # 2x2 matrix
        self.translation_vector = transform_matrix[2, :]     # 2x1 vector
        
        self.is_calibrated = True
        
        logger.info("Calibration complete!")
        logger.info(f"Matrix:\n{self.calibration_matrix}")
        logger.info(f"Translation: {self.translation_vector}")
        logger.info(f"Residuals: {residuals}")
    
    def apply_calibration(self, gaze_x: float, gaze_y: float) -> Tuple[float, float]:
        """
        Apply calibration to raw gaze coordinates
        
        Args:
            gaze_x: Raw horizontal gaze ratio (0.0 - 1.0)
            gaze_y: Raw vertical gaze ratio (0.0 - 1.0)
            
        Returns:
            Calibrated (screen_x, screen_y) in normalized coordinates (0.0 - 1.0)
        """
        if not self.is_calibrated:
            # No calibration, return raw values
            return (gaze_x, gaze_y)
        
        # Apply affine transformation
        gaze_vector = np.array([gaze_x, gaze_y], dtype=np.float32)
        screen_vector = self.calibration_matrix @ gaze_vector + self.translation_vector
        
        # Clamp to [0, 1] range
        screen_x = np.clip(screen_vector[0], 0.0, 1.0)
        screen_y = np.clip(screen_vector[1], 0.0, 1.0)
        
        return (float(screen_x), float(screen_y))
    
    def save_calibration(self, filepath: Path):
        """Save calibration parameters to file"""
        if not self.is_calibrated:
            logger.warning("No calibration to save")
            return
        
        data = {
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'calibration_matrix': self.calibration_matrix.tolist(),
            'translation_vector': self.translation_vector.tolist(),
            'target_positions': self.target_positions,
            'sample_counts': {i: len(self.samples[i]) for i in range(5)}
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Calibration saved to {filepath}")
    
    def load_calibration(self, filepath: Path) -> bool:
        """
        Load calibration parameters from file
        
        Returns:
            True if successfully loaded
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verify screen dimensions match
            if (data['screen_width'] != self.screen_width or 
                data['screen_height'] != self.screen_height):
                logger.warning(
                    f"Screen dimensions mismatch: "
                    f"saved=({data['screen_width']}, {data['screen_height']}), "
                    f"current=({self.screen_width}, {self.screen_height})"
                )
                return False
            
            self.calibration_matrix = np.array(data['calibration_matrix'], dtype=np.float32)
            self.translation_vector = np.array(data['translation_vector'], dtype=np.float32)
            self.is_calibrated = True
            
            logger.info(f"Calibration loaded from {filepath}")
            return True
            
        except FileNotFoundError:
            logger.info(f"No calibration file found at {filepath}")
            return False
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
            return False
    
    def reset(self):
        """Reset calibration state"""
        self.samples = {i: [] for i in range(5)}
        self.current_target_index = 0
        self.is_calibrated = False
        self.calibration_matrix = None
        self.translation_vector = None
        logger.info("Calibration reset")
    
    def get_progress(self) -> Dict:
        """Get calibration progress information"""
        return {
            'current_target': self.current_target_index,
            'total_targets': len(self.target_positions),
            'current_samples': len(self.samples.get(self.current_target_index, [])),
            'required_samples': self.min_samples_per_target,
            'is_complete': self.is_calibrated,
            'target_position': self.get_current_target_position()
        }
