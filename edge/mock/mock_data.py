"""
Mock 데이터 - 실제 서버 없이 UI 테스트용 가상 디바이스 및 추천 데이터
"""
import random
from datetime import datetime


# Mock 디바이스 목록 - 테스트용 2개 디바이스
MOCK_DEVICES = [
    {
        "device_id": "ac_living_room",
        "device_type": "air_conditioner",
        "device_name": "거실 에어컨",
        "display_name": "거실 에어컨",
        "name": "거실 에어컨",
        "capabilities": ["on_off", "temperature", "mode", "fan_speed"],
        "current_state": {
            "is_on": False,
            "temperature": 24,
            "mode": "cool",
            "fan_speed": "auto"
        },
        "location": "living_room",
        "brand": "LG"
    },
    {
        "device_id": "air_purifier_living_room",
        "device_type": "air_purifier",
        "device_name": "공기청정기",
        "display_name": "공기청정기",
        "name": "공기청정기",
        "capabilities": ["on_off", "fan_speed", "mode", "air_quality"],
        "current_state": {
            "is_on": False,
            "fan_speed": "auto",
            "mode": "auto",
            "air_quality": "good",
            "pm25": 15
        },
        "location": "living_room",
        "brand": "Coway"
    }
]


# Mock 추천 목록
MOCK_RECOMMENDATIONS = [
    {
        "recommendation_id": "rec_001",
        "device_id": "ac_living_room",
        "prompt_text": "현재 온도가 높습니다. 에어컨을 시원하게 켜시겠습니까?",
        "message": "현재 온도가 높습니다. 에어컨을 시원하게 켜시겠습니까?",
        "action": {
            "device_id": "ac_living_room",
            "command": "turn_on",
            "parameters": {
                "temperature": 22,
                "mode": "cool",
                "fan_speed": "auto"
            }
        },
        "intent": "turn_on_ac",
        "confidence": 0.92,
        "reasoning": "실내 온도가 높고 에어컨이 꺼진 상태이므로 냉방 모드로 켜는 것을 추천"
    },
    {
        "recommendation_id": "rec_002",
        "device_id": "air_purifier_living_room",
        "prompt_text": "미세먼지 농도가 높습니다. 공기청정기를 켜시겠습니까?",
        "message": "미세먼지 농도가 높습니다. 공기청정기를 켜시겠습니까?",
        "action": {
            "device_id": "air_purifier_living_room",
            "command": "turn_on",
            "parameters": {
                "fan_speed": "high",
                "mode": "auto"
            }
        },
        "intent": "turn_on_air_purifier",
        "confidence": 0.88,
        "reasoning": "외부 미세먼지 농도가 높은 상태"
    }
]


class MockAIClient:
    """테스트용 Mock AI 서비스 클라이언트"""
    
    def __init__(self, base_url: str, user_uuid: str):
        self.base_url = base_url
        self.user_uuid = user_uuid
        self.session = None
        self.recommendation_index = 0
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def get_devices(self):
        """Mock 디바이스 반환"""
        return MOCK_DEVICES.copy()
    
    async def send_device_click(self, device_info: dict, context: dict = None):
        """클릭된 디바이스에 대한 Mock 추천 반환"""
        # 이 디바이스에 대한 추천 찾기
        rec = None
        for r in MOCK_RECOMMENDATIONS:
            if r['device_id'] == device_info.get('device_id'):
                rec = r.copy()
                break
        
        if not rec:
            # 일반 추천
            rec = {
                "recommendation_id": f"rec_{random.randint(100, 999)}",
                "device_id": device_info.get('device_id'),
                "prompt_text": f"{device_info.get('display_name', '기기')}를 제어하시겠습니까?",
                "action": {
                    "device_id": device_info.get('device_id'),
                    "command": "toggle",
                    "parameters": {}
                },
                "intent": "device_control",
                "confidence": 0.75,
                "reasoning": "사용자가 기기를 선택함"
            }
        
        return {
            "status": "success",
            "recommendation": rec,
            "session_id": f"session_{datetime.now().timestamp()}"
        }
    
    async def poll_recommendation(self):
        """주기적으로 Mock 추천 반환"""
        # 10번 호출마다 추천 반환 (주기적 폴링 시뮬레이션)
        self.recommendation_index += 1
        if self.recommendation_index % 10 == 0:
            rec = random.choice(MOCK_RECOMMENDATIONS)
            return rec.copy()
        return None
    
    async def respond_to_recommendation(self, recommendation_id: str, answer: str, device_id: str = None):
        """추천에 대한 Mock 응답"""
        return {
            "status": "success",
            "message": f"Recommendation {answer}",
            "recommendation_id": recommendation_id
        }
    
    async def control_device(self, device_id: str, action: str, parameters: dict = None):
        """Mock 디바이스 제어 - 디바이스 상태 업데이트"""
        # 디바이스를 찾아 상태 토글
        for device in MOCK_DEVICES:
            if device['device_id'] == device_id:
                state = device['current_state']
                
                if action in ['toggle', 'turn_on', 'turn_off']:
                    if action == 'toggle':
                        state['is_on'] = not state.get('is_on', False)
                    elif action == 'turn_on':
                        state['is_on'] = True
                    elif action == 'turn_off':
                        state['is_on'] = False
                
                if parameters:
                    state.update(parameters)
                
                return {
                    "result": "success",
                    "executed_action": action,
                    "updated_state": state,
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "result": "error",
            "message": "Device not found"
        }
    
    async def health_check(self):
        """Mock 모드에서는 항상 정상"""
        return True
