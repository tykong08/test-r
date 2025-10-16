# 🎯 GazeHome Complete Demo Workflow

This guide walks through the complete end-to-end demo of the GazeHome system.

## 📋 Prerequisites Checklist

- [ ] Gateway server running on port 8001
- [ ] AI Service running on port 8000
- [ ] Edge device setup complete
- [ ] Camera connected and working
- [ ] dlib model downloaded

## 🚀 Step-by-Step Demo

### 1. Start All Services

**Terminal 1: Gateway Server**
```bash
cd gateway-main
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8001"
```

**Terminal 2: AI Service**
```bash
cd ai-services-main
python main.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"
```

**Terminal 3: Edge Device**
```bash
cd edge
python run.py
# Should see: "Uvicorn running on http://0.0.0.0:5000"
```

### 2. Verify Services

Open these URLs in browser:
- Gateway Health: http://localhost:8001/health
- AI Service Status: http://localhost:8000/api/gaze/status
- Edge Device UI: http://localhost:5000

### 3. Initial Calibration (First Time Only)

1. **Open Edge Device UI**: http://localhost:5000
2. **Click "시선 보정 시작"** button
3. **Follow calibration process**:
   - Look at top-left red dot (hold for 2-3 seconds)
   - Look at top-right red dot
   - Look at center red dot
   - Look at bottom-left red dot
   - Look at bottom-right red dot
4. **Calibration complete!** 
   - Message: "시선 보정이 완료되었습니다!"
   - Badge changes to "보정 완료"

### 4. Device Control via Gaze Click

**Scenario: Turn on the air conditioner**

1. **Look at the air conditioner card** (거실 에어컨)
2. **Hold your gaze steady** for ~0.8 seconds
   - You'll see a growing red circle around your gaze point
3. **Dwell click triggers** automatically
4. **AI recommendation appears**:
   ```
   💡 AI 추천
   
   현재 오후 2시입니다. 에어컨을 시원하게 켜시겠습니까?
   
   [YES]  [NO]
   ```
5. **Click YES** (with gaze or mouse)
6. **Device control executes**:
   - Request sent to Gateway
   - Gateway controls actual device (or mock)
   - State updates
   - UI refreshes automatically

### 5. View Updated Device State

- Air conditioner card now shows:
  - Status indicator: 🟢 (green)
  - Temperature: 22°C
  - Mode: cool

### 6. AI Recommendation Flow

**Example recommendation triggers:**

**Time-based:**
- Morning (7 AM): "거실 조명을 밝게 켜시겠습니까?"
- Evening (6 PM): "거실 조명을 은은하게 켜시겠습니까?"

**Weather-based (via MCP):**
- Hot day: "에어컨을 시원하게 설정하시겠습니까?"
- Rainy: "에어컨을 제습 모드로 하시겠습니까?"

**State-based:**
- Device off → "켜시겠습니까?"
- Device on → "끄시겠습니까?"

### 7. Manual Device Refresh

- Click **"기기 새로고침"** button
- Fetches latest state from Gateway
- Updates all device cards

## 🎬 Demo Scenarios

### Scenario 1: Morning Routine

**Time**: 7:00 AM

1. Gaze-click **거실 조명**
2. AI suggests: "좋은 아침입니다! 조명을 밝게 켜시겠습니까?"
3. Click YES
4. Lights turn on at 100% brightness

### Scenario 2: Hot Afternoon

**Time**: 2:00 PM, Weather: 32°C, Sunny

1. Gaze-click **거실 에어컨**
2. AI suggests: "현재 기온이 높습니다. 에어컨을 22도로 켜시겠습니까?"
3. Click YES
4. AC turns on, set to 22°C, cool mode

### Scenario 3: Movie Time

**Time**: 8:00 PM

1. Gaze-click **거실 TV**
2. AI suggests: "TV를 켜고 조명을 어둡게 하시겠습니까?"
3. Click YES
4. TV turns on, lights dim to 30%

### Scenario 4: Bedtime

**Time**: 11:00 PM

1. Gaze-click **거실 조명**
2. AI suggests: "취침 시간입니다. 모든 조명을 끄시겠습니까?"
3. Click YES
4. All lights turn off

## 📊 Monitoring & Debugging

### Check Logs

**Edge Device:**
```bash
# In Terminal 3, you'll see:
INFO: GazeTracker initialized: 1920x1080
INFO: Loaded existing calibration
INFO: Device clicked: ac_living_room - toggle at (640, 200)
INFO: Recommendation received: 현재 오후 2시입니다...
```

**AI Service:**
```bash
# In Terminal 2, you'll see:
INFO: 기기 클릭 처리: ac_living_room
INFO: LLM 추천 생성 완료
INFO: 추천 응답: YES
```

**Gateway:**
```bash
# In Terminal 1, you'll see:
INFO: Device control: ac_living_room - turn_on
INFO: Control result: success
```

### WebSocket Connection

Open browser console (F12) on Edge Device page:
```javascript
// You should see:
WebSocket connected
Devices refreshed: {count: 6}
```

### API Testing

**Test Gateway:**
```bash
curl http://localhost:8001/v1/devices
```

**Test AI Service:**
```bash
curl http://localhost:8000/api/gaze/status
```

## 🐛 Common Issues

### Issue: Calibration Not Working

**Symptoms**: Gaze pointer way off target

**Solutions**:
1. Recalibrate (click "시선 보정 시작" again)
2. Ensure good lighting
3. Keep head still during calibration
4. Sit at consistent distance from screen

### Issue: No Devices Showing

**Symptoms**: Empty device grid

**Solutions**:
1. Check Gateway is running: `curl http://localhost:8001/health`
2. Click "기기 새로고침"
3. Check Gateway logs for errors
4. Verify `config.json` has correct Gateway URL

### Issue: Recommendations Not Appearing

**Symptoms**: Click works but no AI popup

**Solutions**:
1. Check AI Service is running: `curl http://localhost:8000/api/gaze/status`
2. Check browser console for errors
3. Verify `config.json` has correct AI Service URL
4. Check AI Service logs

### Issue: Dwell Click Too Sensitive/Slow

**Solution**: Adjust dwell time in `config.json`:
```json
{
  "gaze": {
    "dwell_time": 0.6  // Faster (or 1.0 for slower)
  }
}
```

## 📈 Performance Tips

### For Raspberry Pi

1. **Lower camera resolution** (edit `app.py`):
```python
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

2. **Increase polling intervals** (`config.json`):
```json
{
  "polling": {
    "device_status_interval": 10.0,
    "recommendation_interval": 5.0
  }
}
```

3. **Reduce frame rate** (edit `app.py`):
```python
# In generate_frames(), add:
time.sleep(0.033)  # ~30 fps instead of max
```

## 🎓 Advanced Features

### Custom Device Layouts

Edit device positions by modifying AOI layout in `app.py`:

```python
# Custom 2-column layout
cols = 2
card_width = config.screen_width // cols
```

### Custom Dwell Progress Indicator

Edit `static/style.css` to change dwell indicator appearance:

```css
.dwell-progress {
    border: 4px solid #00ff00;  /* Change color */
    width: 80px;  /* Change size */
}
```

### Add Custom Device Types

Add icons in `static/app.js`:

```javascript
const labels = {
    'custom_device': '🔧 Custom Device'
};
```

## 📝 Data Persistence

### Calibration Data

Stored in: `edge/calibration_params.json`

```json
{
  "screen_width": 1920,
  "screen_height": 1080,
  "calibration_matrix": [[...], [...]],
  "translation_vector": [...]
}
```

### User UUID

Single UUID used across all services: `8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99`

Stored in: `edge/config.json`

## 🎯 Success Criteria

Demo is successful when:

- ✅ Calibration completes all 5 points
- ✅ Gaze pointer tracks eye movement accurately
- ✅ Dwell click triggers on device cards
- ✅ AI recommendation popup appears
- ✅ YES response executes device control
- ✅ Device state updates in UI
- ✅ All operations use single UUID

## 🎉 Demo Complete!

You've successfully demonstrated:

1. **5-point gaze calibration** with affine transformation
2. **Dwell-time based gaze clicking** with visual feedback
3. **Device discovery and control** via Gateway API
4. **AI-powered recommendations** with LLM intent analysis
5. **Real-time UI updates** via WebSocket
6. **End-to-end flow** from gaze → click → AI → control → state update

**Next steps**: Customize for your specific devices, add more AI patterns, optimize for your hardware!

---

**Questions or Issues?** Check `edge/README.md` for detailed documentation.
