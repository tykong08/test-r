"""
시선 추적 메인 클래스 - dlib 기반 얼굴/눈 감지 및 동공 위치 추적
"""
from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration


class GazeTracking(object):
    """
    사용자의 시선을 추적하는 클래스
    눈과 동공의 위치 등 유용한 정보를 제공하고 눈이 열려 있는지 닫혀 있는지 알 수 있습니다
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()

        # _face_detector는 얼굴을 감지하는 데 사용됩니다
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor는 주어진 얼굴의 랜드마크를 가져오는 데 사용됩니다
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        """동공이 위치했는지 확인"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        """얼굴을 감지하고 Eye 객체를 초기화"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """프레임을 새로고침하고 분석합니다

        Arguments:
            frame (numpy.ndarray): 분석할 프레임
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """왼쪽 동공의 좌표 반환"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """오른쪽 동공의 좌표 반환"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)
    
    def pupil_center_coords(self):
        """두 동공 사이의 중심점 좌표 반환"""
        if self.pupils_located:
            left = self.pupil_left_coords()
            right = self.pupil_right_coords()
            center_x = int((left[0] + right[0]) / 2)
            center_y = int((left[1] + right[1]) / 2)
            return (center_x, center_y)

    def horizontal_ratio(self):
        """시선의 수평 방향을 나타내는 0.0과 1.0 사이의 숫자 반환
        가장 오른쪽은 0.0, 중앙은 0.5, 가장 왼쪽은 1.0입니다
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def vertical_ratio(self):
        """시선의 수직 방향을 나타내는 0.0과 1.0 사이의 숫자 반환
        가장 위는 0.0, 중앙은 0.5, 가장 아래는 1.0입니다
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            return (pupil_left + pupil_right) / 2

    def is_right(self):
        """사용자가 오른쪽을 보고 있으면 True 반환"""
        if self.pupils_located:
            return self.horizontal_ratio() <= 0.35

    def is_left(self):
        """사용자가 왼쪽을 보고 있으면 True 반환"""
        if self.pupils_located:
            return self.horizontal_ratio() >= 0.65

    def is_center(self):
        """사용자가 중앙을 보고 있으면 True 반환"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """사용자가 눈을 감으면 True 반환"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 3.8

    def annotated_frame(self):
        """동공이 강조 표시된 메인 프레임 반환"""
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)
            # 두 눈의 중간점만 표시
            center_x, center_y = self.pupil_center_coords()
            # 십자선으로 중간점 표시
            cv2.line(frame, (center_x - 8, center_y), (center_x + 8, center_y), color, 2)
            cv2.line(frame, (center_x, center_y - 8), (center_x, center_y + 8), color, 2)
            # 중심에 원 추가
            cv2.circle(frame, (center_x, center_y), 4, color, -1)

        return frame
