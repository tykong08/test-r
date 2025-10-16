"""
Edge Device 기능 테스트 - 설정 로딩, 보정, API 클라이언트 검증
"""
import asyncio
import json
from pathlib import Path
import sys

# 부모 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from gaze.calibrator import GazeCalibrator


async def test_calibrator():
    """캘리브레이션 시스템 테스트"""
    print("\n=== Testing Calibration System ===")
    
    calibrator = GazeCalibrator(1920, 1080)
    
    # 각 타겟에 대한 샘플 추가 시뮬레이션
    for target_idx in range(5):
        print(f"\nTarget {target_idx + 1}/5")
        target_pos = calibrator.get_current_target_position()
        print(f"  Position: {target_pos}")
        
        # 약간의 변동이 있는 30개 샘플 시뮬레이션
        import random
        base_x = target_pos[0] / 1920
        base_y = target_pos[1] / 1080
        
        for _ in range(30):
            # 랜덤 변동 추가
            x = base_x + random.uniform(-0.02, 0.02)
            y = base_y + random.uniform(-0.02, 0.02)
            calibrator.add_sample(x, y)
        
        print(f"  Collected {len(calibrator.samples[target_idx])} samples")
        
        # 다음 타겟으로 이동
        is_complete = calibrator.move_to_next_target()
        if is_complete:
            print("\n✅ Calibration complete!")
            break
    
    # 캘리브레이션 적용 테스트
    test_point = (0.5, 0.5)
    calibrated = calibrator.apply_calibration(*test_point)
    print(f"\nTest point {test_point} -> {calibrated}")
    
    # 캘리브레이션 저장
    test_file = Path(__file__).parent / "test_calibration.json"
    calibrator.save_calibration(test_file)
    print(f"\n✅ Calibration saved to {test_file}")
    
    # 캘리브레이션 로드
    new_calibrator = GazeCalibrator(1920, 1080)
    success = new_calibrator.load_calibration(test_file)
    print(f"✅ Calibration loaded: {success}")
    
    # 정리
    if test_file.exists():
        test_file.unlink()


async def test_api_clients():
    """API 클라이언트 테스트"""
    print("\n=== Testing API Clients ===")
    
    from api.ai_client import AIServiceClient
    
    # AI 서비스 클라이언트 테스트
    print("\nTesting AI Service Client...")
    async with AIServiceClient(config.ai_service_url, config.user_uuid) as ai:
        health = await ai.health_check()
        print(f"  AI Service health: {health}")
        
        if health:
            # AI Service를 통해 디바이스 가져오기 테스트
            devices = await ai.get_devices()
            if devices:
                print(f"  Found {len(devices)} devices via AI Service")
            else:
                print("  No devices found (AI Service might not be running)")


async def test_config():
    """설정 테스트"""
    print("\n=== Testing Configuration ===")
    
    print(f"User UUID: {config.user_uuid}")
    print(f"AI Service URL: {config.ai_service_url}")
    print(f"Mock Mode: {config.mock_mode}")
    print(f"Dwell time: {config.dwell_time}s")
    print(f"Screen: {config.screen_width}x{config.screen_height}")
    print(f"Calibration file: {config.calibration_file}")
    
    print("\n✅ Configuration loaded successfully")


async def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("GazeHome Edge Device - Test Suite")
    print("=" * 60)
    
    try:
        await test_config()
        await test_calibrator()
        await test_api_clients()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
