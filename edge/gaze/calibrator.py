"""
5포인트 시선 캘리브레이션 시스템
어파인 변환(affine transformation)을 사용한 5개 타겟 포인트 캘리브레이션 구현
"""
import json
import numpy as np
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class GazeCalibrator:
    """
    어파인 변환을 이용한 5포인트 시선 캘리브레이션
    
    캘리브레이션 포인트:
    - 왼쪽 상단 (0.1, 0.1)
    - 오른쪽 상단 (0.9, 0.1)
    - 중앙 (0.5, 0.5)
    - 왼쪽 하단 (0.1, 0.9)
    - 오른쪽 하단 (0.9, 0.9)
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 5개의 캘리브레이션 타겟 위치 (정규화된 좌표 0-1)
        # 7인치 화면에 최적화: 0.1/0.9 → 0.15/0.85로 조정하여 모서리 부담 감소
        self.target_positions = [
            (0.15, 0.15),   # 왼쪽 상단
            (0.85, 0.15),   # 오른쪽 상단
            (0.5, 0.5),     # 중앙
            (0.15, 0.85),   # 왼쪽 하단
            (0.85, 0.85),   # 오른쪽 하단
        ]
        
        # 각 타겟에 대해 수집된 샘플
        self.samples: Dict[int, List[Tuple[float, float]]] = {i: [] for i in range(5)}
        
        # 캘리브레이션 파라미터 (어파인 변환 행렬)
        self.calibration_matrix: Optional[np.ndarray] = None
        self.translation_vector: Optional[np.ndarray] = None
        
        # 캘리브레이션 상태
        self.current_target_index = 0
        self.is_calibrated = False
        
        # 샘플 수집 파라미터
        self.min_samples_per_target = 30  # 30개 샘플 = 약 3초 (100ms 간격 기준)
        self.max_samples_per_target = 50
        self.stability_threshold = 0.05  # 안정적인 샘플의 최대 표준편차
        
        # 7인치 작은 화면에서는 더 엄격한 안정성 필터링 필요
        if screen_width <= 800:
            self.stability_threshold = 0.04  # 작은 화면에서 더 정밀하게
    
    def get_current_target_position(self) -> Tuple[int, int]:
        """화면 좌표에서 현재 캘리브레이션 타겟 위치 가져오기"""
        if self.current_target_index >= len(self.target_positions):
            return (0, 0)
        
        norm_x, norm_y = self.target_positions[self.current_target_index]
        screen_x = int(norm_x * self.screen_width)
        screen_y = int(norm_y * self.screen_height)
        return (screen_x, screen_y)
    
    def add_sample(self, gaze_x: float, gaze_y: float) -> bool:
        """
        현재 타겟에 대한 시선 샘플 추가
        
        Args:
            gaze_x: 수평 시선 비율 (0.0 - 1.0)
            gaze_y: 수직 시선 비율 (0.0 - 1.0)
            
        Returns:
            현재 타겟에 충분한 샘플이 수집된 경우 True
        """
        if self.current_target_index >= len(self.target_positions):
            return False
        
        self.samples[self.current_target_index].append((gaze_x, gaze_y))
        
        # 충분한 샘플이 수집되었는지 확인
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
            # 캘리브레이션 없음, 원시 값 반환
            return (gaze_x, gaze_y)
        
        # 어파인 변환 적용
        gaze_vector = np.array([gaze_x, gaze_y], dtype=np.float32)
        screen_vector = self.calibration_matrix @ gaze_vector + self.translation_vector
        
        # [0, 1] 범위로 제한
        screen_x = np.clip(screen_vector[0], 0.0, 1.0)
        screen_y = np.clip(screen_vector[1], 0.0, 1.0)
        
        return (float(screen_x), float(screen_y))
    
    def save_calibration(self, filepath: Path):
        """캘리브레이션 파라미터를 파일에 저장"""
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
        파일에서 캘리브레이션 파라미터 로드
        
        Returns:
            성공적으로 로드된 경우 True
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 화면 크기가 일치하는지 확인
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
        """캘리브레이션 상태 초기화"""
        self.samples = {i: [] for i in range(5)}
        self.current_target_index = 0
        self.is_calibrated = False
        self.calibration_matrix = None
        self.translation_vector = None
        logger.info("Calibration reset")
    
    def get_progress(self) -> Dict:
        """캘리브레이션 진행 정보 가져오기"""
        return {
            'current_target': self.current_target_index,
            'total_targets': len(self.target_positions),
            'current_samples': len(self.samples.get(self.current_target_index, [])),
            'required_samples': self.min_samples_per_target,
            'is_complete': self.is_calibrated,
            'target_position': self.get_current_target_position()
        }
