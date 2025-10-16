"""
GazeHome Edge Device - 메인 웹 서버
====================================
시선 추적 기반 스마트홈 제어 시스템의 핵심 서버입니다.

주요 기능:
- FastAPI 기반 웹 서버 및 REST API 제공
- WebSocket을 통한 실시간 시선 데이터 스트리밍
- 시선 보정(Calibration) 프로세스 관리
- 스마트홈 디바이스 제어 및 상태 관리
- AI 서비스와의 연동 (추천 시스템)
- 웹캠 영상 스트리밍 및 시선 추적

의존성:
- FastAPI: 웹 서버 프레임워크
- OpenCV: 카메라 제어 및 영상 처리
- WebSocket: 실시간 양방향 통신
- GazeTracker: 시선 추적 엔진

작성자: GazeHome Team
용도: 신체 장애인을 위한 접근성 향상 솔루션
"""
import asyncio
import cv2
import logging
import json
from pathlib import Path
from typing import Dict, Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np

from core.config import config
from gaze.tracker import GazeTracker
from api.ai_client import AIServiceClient
from mock.mock_data import MockAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
gaze_tracker: Optional[GazeTracker] = None
ai_client: Optional[AIServiceClient] = None
camera = None
devices_cache: List[Dict] = []
current_recommendation: Optional[Dict] = None

# Background tasks
background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 및 종료 시 실행되는 이벤트 핸들러"""
    # 시작
    await initialize_services()
    
    # 백그라운드 작업 시작
    task1 = asyncio.create_task(device_polling_task())
    task2 = asyncio.create_task(recommendation_polling_task())
    
    background_tasks.add(task1)
    background_tasks.add(task2)
    
    # 디바이스 즉시 새로고침
    await refresh_devices()
    
    logger.info("✅ Server ready at http://localhost:8000")
    
    yield
    
    # 종료
    global camera
    
    # 백그라운드 작업 취소
    for task in background_tasks:
        task.cancel()
    
    # 카메라 닫기
    if camera:
        camera.release()
    
    # AI 서비스 클라이언트 닫기
    if ai_client and ai_client.session:
        await ai_client.session.close()
    
    logger.info("👋 Shutdown complete")


# Initialize FastAPI with lifespan
app = FastAPI(title="GazeHome Edge Device", lifespan=lifespan)

# Setup templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"
templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


async def initialize_services():
    """모든 필수 서비스 초기화"""
    global ai_client, gaze_tracker, devices_cache, camera
    
    logger.info("Initializing GazeHome Edge Device...")
    
    # AI 서비스 클라이언트 초기화 (mock 또는 실제)
    if config.mock_mode:
        logger.info("🎭 Running in MOCK MODE - using dummy data")
        ai_client = MockAIClient(config.ai_service_url, config.user_uuid)
    else:
        ai_client = AIServiceClient(config.ai_service_url, config.user_uuid)
    
    # AI 서비스 사용 가능 여부 확인 (mock 모드에서는 건너뛰기)
    if not config.mock_mode:
        healthy = await ai_client.health_check()
        if not healthy:
            logger.error("AI Service is not available")
            raise Exception("AI Service connection failed")
    
    # 카메라 초기화 (라즈베리 파이 7인치 + HD 웹캠 최적화)
    logger.info(f"Opening camera at index {config.camera_index}...")
    camera = cv2.VideoCapture(config.camera_index)
    
    if not camera.isOpened():
        logger.error(f"❌ Failed to open camera at index {config.camera_index}")
        logger.info("Try changing camera_index in config.json (0, 1, or 2)")
        # 예외 발생시키지 않음 - 디버깅을 위해 서버 시작 허용
    else:
        # HD 웹캠 설정 적용 (1280x720 @ 30fps)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
        camera.set(cv2.CAP_PROP_FPS, config.camera_fps)
        
        # 실제 적용된 값 확인
        actual_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(camera.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"✅ Camera opened successfully at index {config.camera_index}")
        logger.info(f"📹 Camera resolution: {actual_width}x{actual_height} @ {actual_fps}fps")
        logger.info(f"🖥️  Display resolution: {config.screen_width}x{config.screen_height}")
        
        if config.is_raspberry_pi:
            logger.info(f"🍓 Raspberry Pi mode with 7-inch display")
    
    # 시선 추적기 초기화
    # click_mode='both'는 응시(dwell)와 깜빡임(blink) 감지 모두 활성화
    gaze_tracker = GazeTracker(
        screen_width=config.screen_width,
        screen_height=config.screen_height,
        dwell_time=config.dwell_time,
        camera_index=config.camera_index,
        click_mode='both'  # 항상 두 가지 클릭 방식 모두 활성화
    )
    
    # 초기 디바이스 로드
    await refresh_devices()
    
    logger.info(f"✅ Services initialized successfully ({len(devices_cache)} devices loaded)")
    logger.info(f"UUID: {config.user_uuid}")
    logger.info(f"AI Service: {config.ai_service_url}")
    logger.info(f"Mock Mode: {config.mock_mode}")
    logger.info(f"Click Mode: both (dwell + blink)")
    logger.info(f"Camera Status: {'OPEN' if camera and camera.isOpened() else 'CLOSED'}")


async def on_device_click(device_id: str, action: str, position: tuple):
    """디바이스 클릭 이벤트 처리"""
    global current_recommendation
    
    logger.info(f"Device clicked: {device_id} - {action} at {position}")
    
    # 캐시에서 디바이스 정보 찾기
    device_info = None
    for device in devices_cache:
        if device.get('device_id') == device_id:
            device_info = device
            break
    
    if not device_info:
        logger.warning(f"Device {device_id} not found in cache")
        return
    
    # AI 서비스에 전송하여 추천 받기
    try:
        result = await ai_client.send_device_click(
            device_info=device_info,
            context={'click_position': position}
        )
        
        if result and 'recommendation' in result:
            current_recommendation = result['recommendation']
            current_recommendation['device_id'] = device_id
            current_recommendation['action'] = action
            logger.info(f"Recommendation received: {current_recommendation.get('prompt_text', '')}")
    
    except Exception as e:
        logger.error(f"Error sending click to AI service: {e}")


async def refresh_devices():
    """디바이스 목록 새로고침 및 AOI 업데이트 (AI Service를 통해)"""
    global devices_cache
    
    try:
        # AI Service를 통해 디바이스 가져오기 (Gateway와 통신)
        devices = await ai_client.get_devices()
        
        if devices:
            devices_cache = devices
            
            # 시선 추적기의 AOI 업데이트
            gaze_tracker.clear_aois()
            
            # 디바이스를 위한 그리드 레이아웃 생성 (예: 3열)
            cols = 3
            card_width = config.screen_width // cols
            card_height = 200
            
            for i, device in enumerate(devices):
                row = i // cols
                col = i % cols
                
                x = col * card_width
                y = row * card_height
                
                gaze_tracker.add_aoi(
                    x, y, card_width, card_height,
                    device.get('device_id', f'device_{i}'),
                    'toggle'
                )
            
            logger.info(f"Refreshed {len(devices)} devices")
    
    except Exception as e:
        logger.error(f"Error refreshing devices: {e}")


async def device_polling_task():
    """디바이스 상태를 주기적으로 폴링하는 백그라운드 작업"""
    while True:
        try:
            await refresh_devices()
            await asyncio.sleep(config.device_status_interval)
        except Exception as e:
            logger.error(f"Error in device polling: {e}")
            await asyncio.sleep(config.device_status_interval)


async def recommendation_polling_task():
    """추천을 주기적으로 폴링하는 백그라운드 작업"""
    global current_recommendation
    
    while True:
        try:
            rec = await ai_client.poll_recommendation()
            if rec:
                current_recommendation = rec
                logger.info(f"New recommendation: {rec.get('message', '')}")
            
            await asyncio.sleep(config.recommendation_interval)
        except Exception as e:
            logger.error(f"Error in recommendation polling: {e}")
            await asyncio.sleep(config.recommendation_interval)


def generate_frames():
    """시선 오버레이가 있는 비디오 프레임 생성"""
    global camera, gaze_tracker
    
    while True:
        if camera is None or not camera.isOpened():
            break
        
        ret, frame = camera.read()
        if not ret:
            logger.warning("Failed to read frame")
            break
        
        # 시선 추적 업데이트
        if gaze_tracker:
            result = gaze_tracker.update(frame)
            
            # 시선 포인터 그리기
            if result.get('gaze_position'):
                x, y = result['gaze_position']
                cv2.circle(frame, (x, y), 15, (0, 255, 0), 2)
                
                # 응시 진행률 그리기
                if result.get('dwell_progress', 0) > 0:
                    radius = int(15 + 20 * result['dwell_progress'])
                    cv2.circle(frame, (x, y), radius, (255, 0, 0), 2)
        
        # 프레임을 JPEG로 인코딩
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "screen_width": config.screen_width,
        "screen_height": config.screen_height
    })


@app.get("/video_feed")
async def video_feed():
    """비디오 스트리밍 엔드포인트"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/state")
async def get_state():
    """현재 애플리케이션 상태 조회"""
    return JSONResponse({
        'calibrated': gaze_tracker.is_calibrated() if gaze_tracker else False,
        'devices': devices_cache,
        'recommendation': current_recommendation,
        'user_uuid': config.user_uuid
    })


@app.post("/api/calibration/start")
async def start_calibration():
    """캘리브레이션 프로세스 시작"""
    if gaze_tracker:
        gaze_tracker.start_calibration()
        return JSONResponse({'status': 'started'})
    return JSONResponse({'status': 'error', 'message': 'Gaze tracker not initialized'})


@app.get("/api/calibration/progress")
async def get_calibration_progress():
    """캘리브레이션 진행 상태 조회"""
    if gaze_tracker:
        return JSONResponse(gaze_tracker.get_calibration_progress())
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/calibration/sample")
async def add_calibration_sample():
    """캘리브레이션 샘플 추가"""
    if gaze_tracker:
        ready = gaze_tracker.add_calibration_sample()
        return JSONResponse({'ready': ready})
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/calibration/next")
async def next_calibration_target():
    """다음 캘리브레이션 타겟으로 이동"""
    if gaze_tracker:
        complete = gaze_tracker.next_calibration_target()
        
        if complete:
            # 캘리브레이션 저장
            gaze_tracker.save_calibration(config.calibration_file)
        
        return JSONResponse({'complete': complete})
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/dwell-time")
async def update_dwell_time(request: Request):
    """클릭 감지를 위한 응시 시간(dwell-time) 업데이트"""
    data = await request.json()
    dwell_time = data.get('dwell_time', 0.8)
    
    if gaze_tracker and gaze_tracker.dwell_detector:
        gaze_tracker.dwell_detector.dwell_time = dwell_time
        logger.info(f"Updated dwell time to {dwell_time}s")
        return JSONResponse({'status': 'success', 'dwell_time': dwell_time})
    
    return JSONResponse({'error': 'Gaze tracker not initialized'}, status_code=400)


@app.post("/api/click-mode")
async def update_click_mode(request: Request):
    """클릭 감지 모드 업데이트 (dwell, blink, 또는 both)"""
    data = await request.json()
    click_mode = data.get('click_mode', 'dwell')
    
    if click_mode not in ['dwell', 'blink', 'both']:
        return JSONResponse({'error': 'Invalid click mode. Must be dwell, blink, or both'}, status_code=400)
    
    if gaze_tracker:
        gaze_tracker.click_mode = click_mode
        logger.info(f"Updated click mode to {click_mode}")
        return JSONResponse({'status': 'success', 'click_mode': click_mode})
    
    return JSONResponse({'error': 'Gaze tracker not initialized'}, status_code=400)


@app.post("/api/devices/refresh")
async def refresh_devices_endpoint():
    """디바이스 목록 수동 새로고침"""
    await refresh_devices()
    return JSONResponse({'status': 'refreshed', 'count': len(devices_cache)})


@app.post("/api/devices/{device_id}/control")
async def control_device(device_id: str, request: Request):
    """AI Service를 통한 디바이스 제어"""
    data = await request.json()
    action = data.get('action', 'toggle')
    parameters = data.get('parameters')
    
    # AI Service에 제어 요청 전송 (Gateway로 전달됨)
    result = await ai_client.control_device(device_id, action, parameters)
    
    # 업데이트된 상태를 가져오기 위해 디바이스 새로고침
    await refresh_devices()
    
    return JSONResponse(result or {'error': 'Control failed'})


@app.post("/api/recommendation/respond")
async def respond_to_recommendation(request: Request):
    """추천에 대한 응답 처리"""
    global current_recommendation
    
    data = await request.json()
    answer = data.get('answer', 'NO')
    
    if not current_recommendation:
        return JSONResponse({'error': 'No pending recommendation'})
    
    rec_id = current_recommendation.get('recommendation_id', 'unknown')
    device_id = current_recommendation.get('device_id')
    
    # AI 서비스에 응답 전송
    result = await ai_client.respond_to_recommendation(rec_id, answer, device_id)
    
    # YES인 경우 AI Service를 통해 액션 실행
    if answer.upper() == 'YES' and 'action' in current_recommendation:
        action_data = current_recommendation['action']
        device_id = action_data.get('device_id')
        command = action_data.get('command')
        parameters = action_data.get('parameters')
        
        if device_id and command:
            # AI Service가 Gateway로 제어 명령 전달
            await ai_client.control_device(device_id, command, parameters)
            await refresh_devices()
    
    # 추천 정보 초기화
    current_recommendation = None
    
    return JSONResponse(result or {'status': 'ok'})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 업데이트를 위한 WebSocket"""
    await websocket.accept()
    logger.info("WebSocket connection opened")
    
    frame_count = 0
    
    try:
        while True:
            frame_count += 1
            
            # 주기적으로 카메라 상태 로깅
            if frame_count % 100 == 0:
                camera_status = "OPEN" if (camera and camera.isOpened()) else "CLOSED"
                logger.info(f"WebSocket frame {frame_count}: Camera={camera_status}, GazeTracker={'OK' if gaze_tracker else 'None'}")
            
            # 최신 프레임 및 시선 데이터 가져오기
            if camera is not None and camera.isOpened() and gaze_tracker:
                ret, frame = camera.read()
                if not ret:
                    if frame_count % 50 == 0:
                        logger.warning("Failed to read frame from camera")
                    await asyncio.sleep(0.05)
                    continue
                
                # 시선 추적 업데이트
                result = gaze_tracker.update(frame)
                
                # 디버깅을 위해 주기적으로 결과 로깅
                if frame_count % 100 == 0:
                    logger.info(f"Gaze result: position={result.get('gaze_position')}, pupils_detected={result.get('pupils_detected')}")
                
                # 시선 위치 전송 (동공이 제대로 감지될 때만)
                if result.get('gaze_position') and result.get('pupils_detected'):
                    await websocket.send_json({
                        'type': 'gaze',
                        'position': {
                            'x': result['gaze_position'][0],
                            'y': result['gaze_position'][1]
                        },
                        'pupils_detected': True
                    })
                elif not result.get('pupils_detected'):
                    # 동공이 감지되지 않으면 포인터 숨김
                    await websocket.send_json({
                        'type': 'gaze',
                        'position': None,
                        'pupils_detected': False
                    })
                
                # 응시 진행률 전송
                if result.get('dwell_progress', 0) > 0:
                    await websocket.send_json({
                        'type': 'dwell',
                        'progress': result['dwell_progress'],
                        'position': {
                            'x': result['gaze_position'][0],
                            'y': result['gaze_position'][1]
                        } if result.get('gaze_position') else None
                    })
                
                # 클릭 이벤트 전송
                if result.get('click_detected'):
                    clicked_device = result.get('clicked_device')
                    await websocket.send_json({
                        'type': 'click',
                        'method': result.get('click_method'),
                        'device_id': clicked_device['device_id'] if clicked_device else None,
                        'device_name': clicked_device.get('device_id') if clicked_device else None,
                        'position': clicked_device.get('position') if clicked_device else None
                    })
            else:
                # 카메라가 준비되지 않음 - 경고 로깅
                if frame_count == 1:
                    logger.warning(f"Camera not ready: camera={'None' if camera is None else ('Open' if camera.isOpened() else 'Closed')}, gaze_tracker={'None' if gaze_tracker is None else 'OK'}")
            
            # 상태 업데이트 전송
            state = {
                'type': 'state',
                'devices': devices_cache,
                'recommendation': current_recommendation,
                'calibrated': gaze_tracker.is_calibrated() if gaze_tracker else False
            }
            
            await websocket.send_json(state)
            await asyncio.sleep(0.05)  # 부드러운 추적을 위해 20 FPS
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
