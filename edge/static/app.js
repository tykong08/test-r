// GazeHome Edge Device Frontend

let ws = null;
let calibrationInProgress = false;
let currentRecommendation = null;
let gazeCanvas = null;
let gazeCtx = null;
let calibrationCanvas = null;
let calibrationCtx = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('GazeHome Edge Device initialized');

    // Setup gaze overlay canvas
    setupGazeCanvas();

    // Connect WebSocket
    connectWebSocket();

    // Setup event listeners
    setupEventListeners();

    // Initial state fetch
    fetchState();

    // Start polling for updates
    setInterval(fetchState, 2000);
});

function setupGazeCanvas() {
    // 전체 화면용 Canvas (메인 비디오 제거로 인해 필요 없음)
    console.log('Gaze canvas setup skipped - using full screen pointer');
    // Canvas는 calibration에서만 사용
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Handle different message types
        if (data.type === 'gaze') {
            updateGazePointer(data);
        } else if (data.type === 'click') {
            handleGazeClick(data);
        } else if (data.type === 'dwell') {
            updateDwellProgress(data);
        } else if (data.type === 'recommendation') {
            showRecommendation(data.recommendation);
        } else {
            handleStateUpdate(data);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);

        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };
}

function setupEventListeners() {
    // Calibration button
    document.getElementById('calibrate-btn').addEventListener('click', startCalibration);

    // Refresh button
    document.getElementById('refresh-btn').addEventListener('click', refreshDevices);

    // Recommendation buttons
    document.getElementById('rec-yes-btn').addEventListener('click', () => respondToRecommendation('YES'));
    document.getElementById('rec-no-btn').addEventListener('click', () => respondToRecommendation('NO'));

    // Dwell-time slider
    const dwellSlider = document.getElementById('dwell-time-slider');
    const dwellValue = document.getElementById('dwell-time-value');

    dwellSlider.addEventListener('input', (e) => {
        const value = parseFloat(e.target.value);
        dwellValue.textContent = value.toFixed(1);
    });

    dwellSlider.addEventListener('change', async (e) => {
        const value = parseFloat(e.target.value);
        await updateDwellTime(value);
    });
}

async function updateDwellTime(dwellTime) {
    try {
        const response = await fetch('/api/dwell-time', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dwell_time: dwellTime })
        });

        if (response.ok) {
            console.log(`Dwell time updated to ${dwellTime}s`);
        } else {
            console.error('Failed to update dwell time');
        }
    } catch (error) {
        console.error('Error updating dwell time:', error);
    }
}

async function fetchState() {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        handleStateUpdate(data);
    } catch (error) {
        console.error('Error fetching state:', error);
    }
}

function handleStateUpdate(data) {
    // Update calibration status
    if (data.calibrated) {
        updateCalibrationStatus(true);
    }

    // Update devices
    if (data.devices) {
        updateDeviceGrid(data.devices);
    }

    // Update recommendation
    if (data.recommendation && !currentRecommendation) {
        showRecommendation(data.recommendation);
    }

    // Update user UUID
    if (data.user_uuid) {
        document.getElementById('user-uuid').textContent = `사용자: ${data.user_uuid}`;
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connection-status');
    if (connected) {
        statusEl.textContent = '연결됨';
        statusEl.classList.add('success');
    } else {
        statusEl.textContent = '연결 끊김';
        statusEl.classList.remove('success');
        statusEl.classList.add('warning');
    }
}

function updateCalibrationStatus(calibrated) {
    const statusEl = document.getElementById('calibration-status');
    if (calibrated) {
        statusEl.textContent = '보정 완료';
        statusEl.classList.add('success');
    } else {
        statusEl.textContent = '보정 필요';
        statusEl.classList.remove('success');
    }
}

function updateDeviceGrid(devices) {
    const grid = document.getElementById('device-grid');

    // Clear existing
    grid.innerHTML = '';

    // Add device cards
    devices.forEach((device, index) => {
        const card = createDeviceCard(device, index);
        grid.appendChild(card);
    });
}

function createDeviceCard(device, index) {
    const card = document.createElement('div');
    card.className = 'device-card';
    card.dataset.deviceId = device.device_id;

    const isOn = device.current_state?.is_on || false;

    card.innerHTML = `
        <h3>${device.display_name || device.name || device.device_id}</h3>
        <div class="device-type">${getDeviceTypeLabel(device.device_type)}</div>
        <div class="device-status">
            <span>상태</span>
            <div class="status-indicator ${isOn ? '' : 'off'}"></div>
        </div>
        ${renderDeviceDetails(device)}
    `;

    // Add click handler (for manual control)
    card.addEventListener('click', () => {
        toggleDevice(device.device_id);
    });

    return card;
}

function getDeviceTypeLabel(type) {
    const labels = {
        'light': '💡 조명',
        'air_conditioner': '❄️ 에어컨',
        'tv': '📺 TV',
        'speaker': '🔊 스피커',
        'thermostat': '🌡️ 온도조절기',
        'fan': '🌀 선풍기',
        'heater': '🔥 히터'
    };

    return labels[type] || `📱 ${type}`;
}

function renderDeviceDetails(device) {
    const state = device.current_state || {};
    let details = '';

    // Temperature
    if (state.temperature !== undefined) {
        details += `<div class="device-detail">온도: ${state.temperature}°C</div>`;
    }

    // Brightness
    if (state.brightness !== undefined) {
        details += `<div class="device-detail">밝기: ${state.brightness}%</div>`;
    }

    // Mode
    if (state.mode) {
        details += `<div class="device-detail">모드: ${state.mode}</div>`;
    }

    return details;
}

async function toggleDevice(deviceId) {
    try {
        const response = await fetch(`/api/devices/${deviceId}/control`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: 'toggle'
            })
        });

        const result = await response.json();
        console.log('Device control result:', result);

        // Refresh state
        await fetchState();
    } catch (error) {
        console.error('Error controlling device:', error);
    }
}

async function startCalibration() {
    calibrationInProgress = true;

    // Show calibration overlay
    const overlay = document.getElementById('calibration-overlay');
    overlay.classList.remove('hidden');

    // Setup calibration canvas
    setupCalibrationCanvas();

    // Start calibration
    try {
        await fetch('/api/calibration/start', { method: 'POST' });

        // Start calibration loop
        calibrationLoop();
    } catch (error) {
        console.error('Error starting calibration:', error);
        calibrationInProgress = false;
        overlay.classList.add('hidden');
    }
}

function setupCalibrationCanvas() {
    // 보정 화면 웹캠 프리뷰용 Canvas
    const calibrationWebcam = document.querySelector('.calibration-webcam');
    const calibrationVideo = document.getElementById('calibration-video');

    if (!calibrationCanvas) {
        calibrationCanvas = document.createElement('canvas');
        calibrationCanvas.id = 'calibration-gaze-canvas';
        calibrationCanvas.style.position = 'absolute';
        calibrationCanvas.style.top = '0';
        calibrationCanvas.style.left = '0';
        calibrationCanvas.style.pointerEvents = 'none';
        calibrationCanvas.style.zIndex = '10';
        calibrationWebcam.appendChild(calibrationCanvas);
        calibrationCtx = calibrationCanvas.getContext('2d');
    }

    // Canvas 크기를 비디오에 맞춤
    const resizeCalibrationCanvas = () => {
        const rect = calibrationVideo.getBoundingClientRect();
        calibrationCanvas.width = rect.width;
        calibrationCanvas.height = rect.height;
        calibrationCanvas.style.width = `${rect.width}px`;
        calibrationCanvas.style.height = `${rect.height}px`;
    };

    resizeCalibrationCanvas();
    setTimeout(resizeCalibrationCanvas, 500);
}

async function calibrationLoop() {
    while (calibrationInProgress) {
        try {
            // Get progress
            const progressResponse = await fetch('/api/calibration/progress');
            const progress = await progressResponse.json();

            if (progress.is_complete) {
                // Calibration complete!
                calibrationInProgress = false;
                document.getElementById('calibration-overlay').classList.add('hidden');
                updateCalibrationStatus(true);
                alert('시선 보정이 완료되었습니다!');
                break;
            }

            // Update UI
            updateCalibrationUI(progress);

            // Add sample
            await fetch('/api/calibration/sample', { method: 'POST' });

            // Check if ready for next target
            if (progress.current_samples >= progress.required_samples) {
                await fetch('/api/calibration/next', { method: 'POST' });
            }

            await sleep(100);
        } catch (error) {
            console.error('Calibration error:', error);
            break;
        }
    }
}

function updateCalibrationUI(progress) {
    // Update target position
    const target = document.getElementById('calibration-target');
    const pos = progress.target_position;
    target.style.left = `${pos[0]}px`;
    target.style.top = `${pos[1]}px`;

    // Update progress bar
    const progressBar = document.getElementById('calibration-progress-bar');
    const percentage = (progress.current_samples / progress.required_samples) * 100;
    progressBar.style.width = `${Math.min(percentage, 100)}%`;

    // Update sample count
    document.getElementById('sample-count').textContent = progress.current_samples;
    document.getElementById('sample-required').textContent = progress.required_samples;
    document.getElementById('current-point').textContent = (progress.current_target || 0) + 1;

    // Update instruction
    const instruction = document.getElementById('calibration-instruction');
    instruction.textContent = `타겟 ${(progress.current_target || 0) + 1} / ${progress.total_targets || 5} - 빨간 점을 응시하세요`;
}

// 시선 포인터 업데이트
function updateGazePointer(data) {
    const pointer = document.getElementById('gaze-pointer');

    if (!data.position) {
        pointer.classList.remove('active');
        if (calibrationCtx && calibrationCanvas) {
            calibrationCtx.clearRect(0, 0, calibrationCanvas.width, calibrationCanvas.height);
        }
        return;
    }

    const { x, y } = data.position;

    // 전체 화면 기준으로 DOM 포인터 업데이트
    pointer.style.left = `${x}px`;
    pointer.style.top = `${y}px`;
    pointer.classList.add('active');

    // 보정 화면 Canvas에 시선 포인터 그리기
    if (calibrationInProgress && calibrationCtx && calibrationCanvas) {
        calibrationCtx.clearRect(0, 0, calibrationCanvas.width, calibrationCanvas.height);

        // 보정 화면 웹캠의 상대 좌표 계산
        const calibrationVideo = document.getElementById('calibration-video');
        const calibrationRect = calibrationVideo.getBoundingClientRect();
        const calibrationRelX = (x / window.innerWidth) * calibrationRect.width;
        const calibrationRelY = (y / window.innerHeight) * calibrationRect.height;

        drawGazePointer(calibrationCtx, calibrationRelX, calibrationRelY, 0.7); // 작은 크기
    }
}

// Canvas에 시선 포인터 그리기
function drawGazePointer(ctx, x, y, scale = 1.0) {
    const radius = 20 * scale;
    const centerRadius = 4 * scale;

    // 외곽 원 (글로우 효과)
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius * 1.5);
    gradient.addColorStop(0, 'rgba(0, 255, 0, 0.4)');
    gradient.addColorStop(0.5, 'rgba(0, 255, 0, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 255, 0, 0)');

    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(x, y, radius * 1.5, 0, Math.PI * 2);
    ctx.fill();

    // 메인 원
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 3 * scale;
    ctx.shadowBlur = 15 * scale;
    ctx.shadowColor = '#00ff00';
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.stroke();

    // 중심점
    ctx.fillStyle = '#00ff00';
    ctx.shadowBlur = 10 * scale;
    ctx.beginPath();
    ctx.arc(x, y, centerRadius, 0, Math.PI * 2);
    ctx.fill();

    // 그림자 제거
    ctx.shadowBlur = 0;
}

// Dwell-time 진행도 업데이트
function updateDwellProgress(data) {
    const progress = document.getElementById('dwell-progress');

    if (!data.position || !data.progress) {
        progress.classList.remove('active');
        return;
    }

    const { x, y } = data.position;

    // 전체 화면 기준으로 위치 설정
    progress.style.left = `${x}px`;
    progress.style.top = `${y}px`;
    progress.classList.add('active');

    // 애니메이션 속도 조정 (progress는 0~1)
    progress.style.animationDuration = `${2 * (1 - data.progress)}s`;
}

// 시선 클릭 이벤트 처리
function handleGazeClick(data) {
    console.log('Gaze click detected:', data);

    // 시각적 피드백
    const pointer = document.getElementById('gaze-pointer');
    pointer.style.border = '3px solid #ff0000';
    setTimeout(() => {
        pointer.style.border = '3px solid #00ff00';
    }, 200);

    // 기기 클릭된 경우
    if (data.device_id) {
        console.log('Device clicked:', data.device_id, data.device_name);

        // 기기 카드 하이라이트
        highlightDevice(data.device_id);
    }
}

// 기기 카드 하이라이트
function highlightDevice(deviceId) {
    const deviceCard = document.querySelector(`[data-device-id="${deviceId}"]`);
    if (deviceCard) {
        deviceCard.style.transform = 'scale(1.05)';
        deviceCard.style.boxShadow = '0 8px 16px rgba(102, 126, 234, 0.4)';

        setTimeout(() => {
            deviceCard.style.transform = '';
            deviceCard.style.boxShadow = '';
        }, 500);
    }
}

function showRecommendation(recommendation) {
    currentRecommendation = recommendation;

    const popup = document.getElementById('recommendation-popup');
    const text = document.getElementById('recommendation-text');

    text.textContent = recommendation.prompt_text || recommendation.message || '추천이 있습니다.';

    popup.classList.remove('hidden');
}

async function respondToRecommendation(answer) {
    if (!currentRecommendation) return;

    try {
        const response = await fetch('/api/recommendation/respond', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                answer: answer
            })
        });

        const result = await response.json();
        console.log('Recommendation response:', result);

        // Hide popup
        document.getElementById('recommendation-popup').classList.add('hidden');
        currentRecommendation = null;

        // Refresh state
        await fetchState();
    } catch (error) {
        console.error('Error responding to recommendation:', error);
    }
}

async function refreshDevices() {
    try {
        const response = await fetch('/api/devices/refresh', { method: 'POST' });
        const result = await response.json();
        console.log('Devices refreshed:', result);

        await fetchState();
    } catch (error) {
        console.error('Error refreshing devices:', error);
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
