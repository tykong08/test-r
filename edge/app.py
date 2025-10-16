"""
Main Web Server for Edge Device
Provides web UI and handles gaze tracking, calibration, and device control
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
from mock_data import MockAIClient

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
    """Lifespan event handler for startup and shutdown"""
    # Startup
    await initialize_services()
    
    # Start background tasks
    task1 = asyncio.create_task(device_polling_task())
    task2 = asyncio.create_task(recommendation_polling_task())
    
    background_tasks.add(task1)
    background_tasks.add(task2)
    
    # Refresh devices immediately
    await refresh_devices()
    
    logger.info("✅ Server ready at http://localhost:8000")
    
    yield
    
    # Shutdown
    global camera
    
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
    
    # Close camera
    if camera:
        camera.release()
    
    # Close AI Service client
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
    """Initialize all required services"""
    global ai_client, gaze_tracker, devices_cache, camera
    
    logger.info("Initializing GazeHome Edge Device...")
    
    # Initialize AI Service client (mock or real)
    if config.mock_mode:
        logger.info("🎭 Running in MOCK MODE - using dummy data")
        ai_client = MockAIClient(config.ai_service_url, config.user_uuid)
    else:
        ai_client = AIServiceClient(config.ai_service_url, config.user_uuid)
    
    # Verify AI service is available (skip health check in mock mode)
    if not config.mock_mode:
        healthy = await ai_client.health_check()
        if not healthy:
            logger.error("AI Service is not available")
            raise Exception("AI Service connection failed")
    
    # Initialize camera
    logger.info(f"Opening camera at index {config.camera_index}...")
    camera = cv2.VideoCapture(config.camera_index)
    
    if not camera.isOpened():
        logger.error(f"❌ Failed to open camera at index {config.camera_index}")
        logger.info("Try changing camera_index in config.json (0, 1, or 2)")
        # Don't raise exception - allow server to start for debugging
    else:
        logger.info(f"✅ Camera opened successfully at index {config.camera_index}")
    
    # Initialize gaze tracker with proper parameters
    # click_mode='both' enables both dwell-time and blink detection
    gaze_tracker = GazeTracker(
        screen_width=config.screen_width,
        screen_height=config.screen_height,
        dwell_time=config.dwell_time,
        camera_index=config.camera_index,
        click_mode='both'  # Always enable both click methods
    )
    
    # Load initial devices
    await refresh_devices()
    
    logger.info(f"✅ Services initialized successfully ({len(devices_cache)} devices loaded)")
    logger.info(f"UUID: {config.user_uuid}")
    logger.info(f"AI Service: {config.ai_service_url}")
    logger.info(f"Mock Mode: {config.mock_mode}")
    logger.info(f"Click Mode: both (dwell + blink)")
    logger.info(f"Camera Status: {'OPEN' if camera and camera.isOpened() else 'CLOSED'}")


async def on_device_click(device_id: str, action: str, position: tuple):
    """Handle device click event"""
    global current_recommendation
    
    logger.info(f"Device clicked: {device_id} - {action} at {position}")
    
    # Find device info from cache
    device_info = None
    for device in devices_cache:
        if device.get('device_id') == device_id:
            device_info = device
            break
    
    if not device_info:
        logger.warning(f"Device {device_id} not found in cache")
        return
    
    # Send to AI service for recommendation
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
    """Refresh device list and update AOIs via AI Service"""
    global devices_cache
    
    try:
        # Get devices from AI Service (which communicates with Gateway)
        devices = await ai_client.get_devices()
        
        if devices:
            devices_cache = devices
            
            # Update AOIs in gaze tracker
            gaze_tracker.clear_aois()
            
            # Create grid layout for devices (example: 3 columns)
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
    """Background task to poll device status"""
    while True:
        try:
            await refresh_devices()
            await asyncio.sleep(config.device_status_interval)
        except Exception as e:
            logger.error(f"Error in device polling: {e}")
            await asyncio.sleep(config.device_status_interval)


async def recommendation_polling_task():
    """Background task to poll for recommendations"""
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
    """Generate video frames with gaze overlay"""
    global camera, gaze_tracker
    
    while True:
        if camera is None or not camera.isOpened():
            break
        
        ret, frame = camera.read()
        if not ret:
            logger.warning("Failed to read frame")
            break
        
        # Update gaze tracking
        if gaze_tracker:
            result = gaze_tracker.update(frame)
            
            # Draw gaze pointer
            if result.get('gaze_position'):
                x, y = result['gaze_position']
                cv2.circle(frame, (x, y), 15, (0, 255, 0), 2)
                
                # Draw dwell progress
                if result.get('dwell_progress', 0) > 0:
                    radius = int(15 + 20 * result['dwell_progress'])
                    cv2.circle(frame, (x, y), radius, (255, 0, 0), 2)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "screen_width": config.screen_width,
        "screen_height": config.screen_height
    })


@app.get("/video_feed")
async def video_feed():
    """Video streaming endpoint"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/api/state")
async def get_state():
    """Get current application state"""
    return JSONResponse({
        'calibrated': gaze_tracker.is_calibrated() if gaze_tracker else False,
        'devices': devices_cache,
        'recommendation': current_recommendation,
        'user_uuid': config.user_uuid
    })


@app.post("/api/calibration/start")
async def start_calibration():
    """Start calibration process"""
    if gaze_tracker:
        gaze_tracker.start_calibration()
        return JSONResponse({'status': 'started'})
    return JSONResponse({'status': 'error', 'message': 'Gaze tracker not initialized'})


@app.get("/api/calibration/progress")
async def get_calibration_progress():
    """Get calibration progress"""
    if gaze_tracker:
        return JSONResponse(gaze_tracker.get_calibration_progress())
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/calibration/sample")
async def add_calibration_sample():
    """Add calibration sample"""
    if gaze_tracker:
        ready = gaze_tracker.add_calibration_sample()
        return JSONResponse({'ready': ready})
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/calibration/next")
async def next_calibration_target():
    """Move to next calibration target"""
    if gaze_tracker:
        complete = gaze_tracker.next_calibration_target()
        
        if complete:
            # Save calibration
            gaze_tracker.save_calibration(config.calibration_file)
        
        return JSONResponse({'complete': complete})
    return JSONResponse({'error': 'Gaze tracker not initialized'})


@app.post("/api/dwell-time")
async def update_dwell_time(request: Request):
    """Update dwell-time for click detection"""
    data = await request.json()
    dwell_time = data.get('dwell_time', 0.8)
    
    if gaze_tracker and gaze_tracker.dwell_detector:
        gaze_tracker.dwell_detector.dwell_time = dwell_time
        logger.info(f"Updated dwell time to {dwell_time}s")
        return JSONResponse({'status': 'success', 'dwell_time': dwell_time})
    
    return JSONResponse({'error': 'Gaze tracker not initialized'}, status_code=400)


@app.post("/api/click-mode")
async def update_click_mode(request: Request):
    """Update click detection mode (dwell, blink, or both)"""
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
    """Manually refresh device list"""
    await refresh_devices()
    return JSONResponse({'status': 'refreshed', 'count': len(devices_cache)})


@app.post("/api/devices/{device_id}/control")
async def control_device(device_id: str, request: Request):
    """Control a device via AI Service"""
    data = await request.json()
    action = data.get('action', 'toggle')
    parameters = data.get('parameters')
    
    # Send control request to AI Service (which forwards to Gateway)
    result = await ai_client.control_device(device_id, action, parameters)
    
    # Refresh devices to get updated state
    await refresh_devices()
    
    return JSONResponse(result or {'error': 'Control failed'})


@app.post("/api/recommendation/respond")
async def respond_to_recommendation(request: Request):
    """Respond to a recommendation"""
    global current_recommendation
    
    data = await request.json()
    answer = data.get('answer', 'NO')
    
    if not current_recommendation:
        return JSONResponse({'error': 'No pending recommendation'})
    
    rec_id = current_recommendation.get('recommendation_id', 'unknown')
    device_id = current_recommendation.get('device_id')
    
    # Send response to AI service
    result = await ai_client.respond_to_recommendation(rec_id, answer, device_id)
    
    # If YES, execute the action via AI Service
    if answer.upper() == 'YES' and 'action' in current_recommendation:
        action_data = current_recommendation['action']
        device_id = action_data.get('device_id')
        command = action_data.get('command')
        parameters = action_data.get('parameters')
        
        if device_id and command:
            # AI Service will forward the control command to Gateway
            await ai_client.control_device(device_id, command, parameters)
            await refresh_devices()
    
    # Clear recommendation
    current_recommendation = None
    
    return JSONResponse(result or {'status': 'ok'})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    logger.info("WebSocket connection opened")
    
    frame_count = 0
    
    try:
        while True:
            frame_count += 1
            
            # Log camera status periodically
            if frame_count % 100 == 0:
                camera_status = "OPEN" if (camera and camera.isOpened()) else "CLOSED"
                logger.info(f"WebSocket frame {frame_count}: Camera={camera_status}, GazeTracker={'OK' if gaze_tracker else 'None'}")
            
            # Get latest frame and gaze data
            if camera is not None and camera.isOpened() and gaze_tracker:
                ret, frame = camera.read()
                if not ret:
                    if frame_count % 50 == 0:
                        logger.warning("Failed to read frame from camera")
                    await asyncio.sleep(0.05)
                    continue
                
                # Update gaze tracking
                result = gaze_tracker.update(frame)
                
                # Log result periodically for debugging
                if frame_count % 100 == 0:
                    logger.info(f"Gaze result: position={result.get('gaze_position')}, pupils_detected={result.get('pupils_detected')}")
                
                # Send gaze position
                if result.get('gaze_position'):
                    await websocket.send_json({
                        'type': 'gaze',
                        'position': {
                            'x': result['gaze_position'][0],
                            'y': result['gaze_position'][1]
                        }
                    })
                
                # Send dwell progress
                if result.get('dwell_progress', 0) > 0:
                    await websocket.send_json({
                        'type': 'dwell',
                        'progress': result['dwell_progress'],
                        'position': {
                            'x': result['gaze_position'][0],
                            'y': result['gaze_position'][1]
                        } if result.get('gaze_position') else None
                    })
                
                # Send click event
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
                # Camera not ready - log warning
                if frame_count == 1:
                    logger.warning(f"Camera not ready: camera={'None' if camera is None else ('Open' if camera.isOpened() else 'Closed')}, gaze_tracker={'None' if gaze_tracker is None else 'OK'}")
            
            # Send state updates
            state = {
                'type': 'state',
                'devices': devices_cache,
                'recommendation': current_recommendation,
                'calibrated': gaze_tracker.is_calibrated() if gaze_tracker else False
            }
            
            await websocket.send_json(state)
            await asyncio.sleep(0.05)  # 20 FPS for smooth tracking
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
