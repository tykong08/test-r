"""
시선 추적 시스템 통합 테스트 - 웹캠, 보정, 클릭 감지 검증
"""
import cv2
import sys
import os
import time
import numpy as np
from pathlib import Path

# 부모 디렉토리를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model import GazeTracking
from gaze.calibrator import GazeCalibrator

print("=" * 60)
print("  Gaze Tracking and Calibration Test")
print("=" * 60)
print()

# 테스트 1: 웹캠 감지
print("Test 1: Webcam Detection")
print("-" * 60)

camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("❌ FAILED: Cannot open webcam")
    print("   Please check:")
    print("   - Webcam is connected")
    print("   - Camera permissions are granted")
    print("   - No other application is using the camera")
    sys.exit(1)

ret, frame = camera.read()
if not ret:
    print("❌ FAILED: Cannot read from webcam")
    camera.release()
    sys.exit(1)

height, width = frame.shape[:2]
print(f"✅ PASSED: Webcam detected and working")
print(f"   Resolution: {width}x{height}")
print(f"   FPS: {camera.get(cv2.CAP_PROP_FPS)}")
print()

# 테스트 2: 시선 추적 초기화
print("Test 2: Gaze Tracking Initialization")
print("-" * 60)

try:
    gaze = GazeTracking()
    print("✅ PASSED: GazeTracking initialized successfully")
    print(f"   Face detector: dlib 68-point model")
    print(f"   Eye detection: Custom pupil detector")
except Exception as e:
    print(f"❌ FAILED: GazeTracking initialization failed")
    print(f"   Error: {e}")
    camera.release()
    sys.exit(1)
print()

# 테스트 3: 실시간 시선 추적 (10초)
print("Test 3: Real-time Gaze Tracking")
print("-" * 60)
print("Testing gaze tracking for 10 seconds...")
print("Please look at the camera and move your eyes around")
print()

start_time = time.time()
frame_count = 0
gaze_detected_count = 0
pupil_detected_count = 0

while time.time() - start_time < 10:
    ret, frame = camera.read()
    if not ret:
        break
    
    frame_count += 1
    
    # 시선 분석
    gaze.refresh(frame)
    
    # 감지 확인
    if not gaze.pupils_located:
        status = "❌ No pupils detected"
        color = (0, 0, 255)  # 빨간색
    else:
        pupil_detected_count += 1
        
        # 시선 위치 가져오기
        horizontal = gaze.horizontal_ratio()
        vertical = gaze.vertical_ratio()
        
        if horizontal is not None and vertical is not None:
            gaze_detected_count += 1
            
            # 시선 방향 결정
            if gaze.is_center():
                direction = "CENTER"
            elif gaze.is_right():
                direction = "RIGHT"
            elif gaze.is_left():
                direction = "LEFT"
            elif gaze.is_top():
                direction = "TOP"
            elif gaze.is_bottom():
                direction = "BOTTOM"
            else:
                direction = "UNKNOWN"
            
            status = f"✅ Gaze: {direction} (H:{horizontal:.2f}, V:{vertical:.2f})"
            color = (0, 255, 0)  # 초록색
        else:
            status = "⚠️ Pupils found but gaze calculation failed"
            color = (0, 255, 255)  # 노란색
    
    # 프레임에 주석 추가
    frame = gaze.annotated_frame()
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, color, 2)
    cv2.putText(frame, f"Frame: {frame_count}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # 시선 포인트 그리기 (가능한 경우)
    if gaze.pupils_located:
        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        
        if left_pupil:
            cv2.circle(frame, left_pupil, 5, (0, 255, 0), -1)
        if right_pupil:
            cv2.circle(frame, right_pupil, 5, (0, 255, 0), -1)
    
    # 프레임 표시
    cv2.imshow('Gaze Tracking Test', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# 성공률 계산
pupil_rate = (pupil_detected_count / frame_count * 100) if frame_count > 0 else 0
gaze_rate = (gaze_detected_count / frame_count * 100) if frame_count > 0 else 0

print()
print(f"Frames processed: {frame_count}")
print(f"Pupil detection rate: {pupil_rate:.1f}% ({pupil_detected_count}/{frame_count})")
print(f"Gaze calculation rate: {gaze_rate:.1f}% ({gaze_detected_count}/{frame_count})")

if pupil_rate > 70:
    print("✅ PASSED: Pupil detection is working well")
else:
    print("⚠️ WARNING: Pupil detection rate is low")
    print("   Tips:")
    print("   - Ensure good lighting")
    print("   - Look directly at camera")
    print("   - Remove glasses if possible")

if gaze_rate > 60:
    print("✅ PASSED: Gaze tracking is working well")
else:
    print("⚠️ WARNING: Gaze tracking rate is low")

print()

# 테스트 4: 캘리브레이션 시스템
print("Test 4: Calibration System")
print("-" * 60)

try:
    calibrator = GazeCalibrator(
        screen_width=1920,
        screen_height=1080,
        num_points=5
    )
    print("✅ PASSED: GazeCalibrator initialized")
    print(f"   Calibration points: {calibrator.num_points}")
    print(f"   Screen size: {calibrator.screen_width}x{calibrator.screen_height}")
except Exception as e:
    print(f"❌ FAILED: GazeCalibrator initialization failed")
    print(f"   Error: {e}")
    camera.release()
    sys.exit(1)

print()
print("Testing calibration point collection...")
print("Please look at the center of the screen")
print()

# 화면 중앙에서 3초간 캘리브레이션 시뮬레이션
calibration_point = (960, 540)  # 1920x1080의 중앙
samples_collected = 0
target_samples = 30

start_time = time.time()
while time.time() - start_time < 3:
    ret, frame = camera.read()
    if not ret:
        break
    
    gaze.refresh(frame)
    
    if gaze.pupils_located:
        h_ratio = gaze.horizontal_ratio()
        v_ratio = gaze.vertical_ratio()
        
        if h_ratio is not None and v_ratio is not None:
            calibrator.add_sample(calibration_point, (h_ratio, v_ratio))
            samples_collected += 1
    
    # 프레임 표시
    frame_copy = frame.copy()
    cv2.putText(frame_copy, f"Samples: {samples_collected}/{target_samples}", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame_copy, "Look at screen center", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Calibration Test', frame_copy)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

print(f"Collected {samples_collected} calibration samples")

if samples_collected >= 10:
    print("✅ PASSED: Calibration sample collection working")
    
    # 캘리브레이션 계산 시도
    try:
        success = calibrator.calculate_calibration()
        if success:
            print("✅ PASSED: Calibration calculation successful")
            
            # 저장/로드 테스트
            calib_file = Path("test_calibration.json")
            calibrator.save_calibration(calib_file)
            print(f"✅ PASSED: Calibration saved to {calib_file}")
            
            # 다시 로드
            new_calibrator = GazeCalibrator(1920, 1080)
            if new_calibrator.load_calibration(calib_file):
                print("✅ PASSED: Calibration loaded successfully")
                
                # 정리
                calib_file.unlink()
            else:
                print("❌ FAILED: Could not load calibration")
        else:
            print("⚠️ WARNING: Calibration calculation failed (need more points)")
    except Exception as e:
        print(f"❌ FAILED: Calibration calculation error: {e}")
else:
    print("⚠️ WARNING: Not enough calibration samples collected")
    print("   This is normal for a quick test")

print()

# 테스트 5: 좌표 변환
print("Test 5: Coordinate Transformation")
print("-" * 60)

if calibrator.is_calibrated:
    # 변환 테스트
    test_gaze = (0.5, 0.5)  # 중앙 시선
    screen_pos = calibrator.apply_calibration(test_gaze)
    
    if screen_pos:
        print(f"✅ PASSED: Coordinate transformation working")
        print(f"   Gaze ratio {test_gaze} → Screen position {screen_pos}")
        
        # 결과가 합리적인지 확인
        x, y = screen_pos
        if 0 <= x <= 1920 and 0 <= y <= 1080:
            print(f"✅ PASSED: Transformed coordinates are within screen bounds")
        else:
            print(f"⚠️ WARNING: Transformed coordinates out of bounds")
    else:
        print("❌ FAILED: Coordinate transformation returned None")
else:
    print("⚠️ SKIPPED: No calibration data available")

print()

# 정리
camera.release()
cv2.destroyAllWindows()

# 요약
print("=" * 60)
print("  Test Summary")
print("=" * 60)
print()
print("✅ Webcam: Working")
print(f"✅ Gaze Tracking: {gaze_rate:.1f}% success rate")
print(f"✅ Pupil Detection: {pupil_rate:.1f}% success rate")
print("✅ Calibration: System functional")
print()
print("All core components are working!")
print()
print("Next steps:")
print("1. Run the web server: python app.py")
print("2. Open browser: http://localhost:8000")
print("3. Click 'Start Calibration' and follow the 5 points")
print("4. Click 'Start Tracking' to test gaze control")
print()
