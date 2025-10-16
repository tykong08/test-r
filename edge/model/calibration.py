"""
동공 감지 임계값 자동 보정 - 개인별/환경별 최적 threshold 값 계산
"""
from __future__ import division
import cv2
from .pupil import Pupil


class Calibration(object):
    """
    동공 감지 알고리즘 보정 클래스
    개인 및 웹캠에 가장 적합한 이진화 임계값을 찾아 보정합니다.
    """

    def __init__(self):
        self.nb_frames = 20
        self.thresholds_left = []
        self.thresholds_right = []

    def is_complete(self):
        """캘리브레이션 완료 여부 반환"""
        return len(self.thresholds_left) >= self.nb_frames and len(self.thresholds_right) >= self.nb_frames

    def threshold(self, side):
        """주어진 눈의 임계값 반환

        Argument:
            side: 왼쪽 눈(0) 또는 오른쪽 눈(1) 표시
        """
        if side == 0:
            return int(sum(self.thresholds_left) / len(self.thresholds_left))
        elif side == 1:
            return int(sum(self.thresholds_right) / len(self.thresholds_right))

    @staticmethod
    def iris_size(frame):
        """눈 표면에서 홍채가 차지하는 공간의 비율 반환

        Argument:
            frame (numpy.ndarray): 이진화된 홍채 프레임
        """
        frame = frame[5:-5, 5:-5]
        height, width = frame.shape[:2]
        nb_pixels = height * width
        nb_blacks = nb_pixels - cv2.countNonZero(frame)
        return nb_blacks / nb_pixels

    @staticmethod
    def find_best_threshold(eye_frame):
        """주어진 눈에 대해 프레임을 이진화할 최적 임계값 계산

        Argument:
            eye_frame (numpy.ndarray): 분석할 눈 프레임
        """
        average_iris_size = 0.48
        trials = {}

        for threshold in range(5, 100, 5):
            iris_frame = Pupil.image_processing(eye_frame, threshold)
            trials[threshold] = Calibration.iris_size(iris_frame)

        best_threshold, iris_size = min(trials.items(), key=(lambda p: abs(p[1] - average_iris_size)))
        return best_threshold

    def evaluate(self, eye_frame, side):
        """주어진 이미지를 고려하여 캘리브레이션 개선

        Arguments:
            eye_frame (numpy.ndarray): 눈 프레임
            side: 왼쪽 눈(0) 또는 오른쪽 눈(1) 표시
        """
        threshold = self.find_best_threshold(eye_frame)

        if side == 0:
            self.thresholds_left.append(threshold)
        elif side == 1:
            self.thresholds_right.append(threshold)
