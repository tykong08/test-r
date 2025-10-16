# 🔄 아키텍처 수정 완료

## 변경 사항 요약

### ✅ 수정 완료

**Edge Device는 이제 Gateway와 직접 통신하지 않습니다.**

모든 기기 관련 요청은 **AI Service를 경유**합니다:

```
Edge Device ──> AI Service ──> Gateway ──> Smart Devices
```

## 수정된 파일

### 1. `edge/app.py`
- ❌ **제거:** `GatewayClient` import 및 사용
- ✅ **변경:** 모든 기기 요청을 `ai_client`로 처리
  - `ai_client.get_devices()` - 기기 목록
  - `ai_client.control_device()` - 기기 제어

### 2. `edge/api/ai_client.py`
- ✅ **추가:** 기기 관련 메서드
  - `async def get_devices()` - AI Service를 통해 기기 목록 조회
  - `async def control_device()` - AI Service를 통해 기기 제어

### 3. `edge/config.json`
- ❌ **제거:** `gateway_url` 설정
- ✅ **유지:** `ai_service_url`만 사용

### 4. `edge/core/config.py`
- ❌ **제거:** `gateway_url` property
- ✅ **유지:** `ai_service_url` property

### 5. `edge/ARCHITECTURE.md`
- ✅ **추가:** 새로운 아키텍처 문서
  - 통신 흐름 다이어그램
  - 데이터 플로우 설명
  - 변경 사항 상세 기록

## 통신 구조

### Before (❌ 잘못됨)
```python
# Edge Device에서 직접 Gateway 호출
devices = await gateway_client.get_devices()
await gateway_client.control_device(id, action)
```

### After (✅ 올바름)
```python
# Edge Device는 AI Service만 호출
devices = await ai_client.get_devices()  # AI → Gateway로 전달
await ai_client.control_device(id, action)  # AI → Gateway로 전달
```

## AI Service에 필요한 엔드포인트

AI Service는 다음 엔드포인트를 제공해야 합니다:

### 기기 관련
```python
@router.get("/devices")
async def get_devices(user_id: str):
    """Edge Device 요청을 Gateway로 전달"""
    # Gateway API 호출
    devices = await gateway.get_devices()
    return {"devices": devices}

@router.post("/devices/control")
async def control_device(data: dict):
    """Edge Device 제어 요청을 Gateway로 전달"""
    # Gateway API 호출
    result = await gateway.control_device(
        device_id=data['device_id'],
        action=data['action'],
        parameters=data.get('parameters')
    )
    return result
```

### 기존 엔드포인트 (유지)
- `POST /api/gaze/click` - 시선 클릭 이벤트
- `GET /v1/intent` - AI 추천 폴링  
- `POST /v1/intent` - YES/NO 응답

## 테스트 방법

### 1. AI Service 엔드포인트 추가 확인
```bash
# ai-services-main/app/api/endpoints/devices.py 확인
# /api/devices GET 엔드포인트가 Gateway와 통신하는지 확인
```

### 2. Edge Device 실행
```bash
cd edge
python run.py
# 브라우저: http://localhost:5000
```

### 3. 동작 확인
- ✅ 기기 목록이 표시되는가? (AI Service → Gateway)
- ✅ 시선 클릭 시 추천이 나타나는가? (AI Service LLM)
- ✅ YES 클릭 시 기기가 제어되는가? (AI Service → Gateway)

## 설정 파일

### edge/config.json
```json
{
  "user_uuid": "8f6b3c54-7b3b-4d4c-9e5d-2e8b1c1d4f99",
  "server": {
    "ai_service_url": "http://localhost:8000"
    // gateway_url 제거됨!
  }
}
```

## 장점

### 1. 보안
- Edge Device는 AI Service만 신뢰
- Gateway 직접 노출 방지
- 중앙 집중식 인증 가능

### 2. 유지보수
- Edge Device 코드 단순화
- 비즈니스 로직은 AI Service에 집중
- Gateway 변경 시 Edge Device 영향 없음

### 3. 확장성
- 여러 Edge Device가 하나의 AI Service 사용
- AI Service에서 부하 분산
- Gateway 클러스터링 용이

## 체크리스트

- [x] Edge Device에서 GatewayClient 제거
- [x] AIServiceClient에 get_devices() 추가
- [x] AIServiceClient에 control_device() 추가
- [x] config.json에서 gateway_url 제거
- [x] config.py에서 gateway_url property 제거
- [x] 아키텍처 문서 작성 (ARCHITECTURE.md)
- [ ] AI Service에 /api/devices 엔드포인트 구현 확인 필요

## 다음 단계

AI Service (`ai-services-main`)에서 다음을 확인/구현해야 합니다:

1. **`/api/devices` GET 엔드포인트**
   - Edge Device 요청 수신
   - Gateway `/v1/devices` 호출
   - 결과 반환

2. **`/api/devices/control` POST 엔드포인트**
   - Edge Device 제어 요청 수신
   - Gateway `/v1/devices/{id}/control` 호출
   - 결과 반환

---

**상태: ✅ Edge Device 수정 완료**

Edge Device는 이제 올바른 아키텍처를 따릅니다!
