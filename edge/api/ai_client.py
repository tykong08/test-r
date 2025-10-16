"""
AI 서비스 HTTP 클라이언트 - 추천 요청 및 응답 처리
"""
import aiohttp
import asyncio
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class AIServiceClient:
    """AI 서비스 API 클라이언트"""
    
    def __init__(self, base_url: str, user_uuid: str):
        self.base_url = base_url.rstrip('/')
        self.user_uuid = user_uuid
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_recommendation: Optional[Dict] = None
        
        logger.info(f"AIServiceClient initialized: {base_url}")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, 
                      json_data: Optional[Dict] = None,
                      params: Optional[Dict] = None,
                      retries: int = 3) -> Optional[Dict]:
        """
        재시도를 포함한 HTTP 요청 수행
        
        Args:
            method: HTTP 메서드 (GET, POST 등)
            endpoint: API 엔드포인트
            json_data: JSON 페이로드
            params: 쿼리 파라미터
            retries: 재시도 횟수
            
        Returns:
            응답 데이터 또는 에러 시 None
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                async with self.session.request(
                    method, url, json=json_data, params=params, 
                    timeout=aiohttp.ClientTimeout(total=30)  # Longer timeout for LLM
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Request failed: {response.status} - {await response.text()}")
                        
                        if attempt < retries - 1:
                            await asyncio.sleep(1)
                        
            except aiohttp.ClientError as e:
                logger.error(f"Request error (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        return None
    
    async def send_device_click(self, device_info: Dict, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        디바이스 클릭 이벤트를 AI 서비스에 전송하여 추천 받기
        
        Args:
            device_info: 클릭된 디바이스 정보
            context: 추가 컨텍스트
            
        Returns:
            AI 서비스로부터의 추천
        """
        payload = {
            'user_id': self.user_uuid,
            'session_id': f"session_{datetime.now().timestamp()}",
            'clicked_device': device_info,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        result = await self._request('POST', '/api/gaze/click', json_data=payload)
        
        if result and 'recommendation' in result:
            self.current_recommendation = result['recommendation']
            # 응답에서 사용 가능한 경우 recommendation_id 추가
            if 'recommendation_id' not in self.current_recommendation and 'session_id' in result:
                self.current_recommendation['recommendation_id'] = result['session_id']
            
            logger.info(f"Received recommendation: {self.current_recommendation.get('prompt_text', '')[:50]}...")
        
        return result
    
    async def poll_recommendation(self) -> Optional[Dict]:
        """
        대기 중인 추천 폴링
        
        Returns:
            사용 가능한 경우 추천
        """
        params = {'user_uuid': self.user_uuid}
        result = await self._request('GET', '/v1/intent', params=params, retries=1)
        
        if result and result.get('status') == 'success':
            # 대기 중인 추천이 있는지 확인
            if 'recommendation' in result:
                self.current_recommendation = result['recommendation']
                logger.info(f"Polled recommendation: {self.current_recommendation.get('message', '')[:50]}...")
                return self.current_recommendation
        
        return None
    
    async def respond_to_recommendation(self, recommendation_id: str, answer: str, 
                                       device_id: Optional[str] = None) -> Optional[Dict]:
        """
        추천에 대한 YES/NO 응답 전송
        
        Args:
            recommendation_id: 추천 ID
            answer: "YES" 또는 "NO"
            device_id: 디바이스 ID (해당되는 경우)
            
        Returns:
            응답 결과
        """
        payload = {
            'user_uuid': self.user_uuid,
            'recommendation_id': recommendation_id,
            'answer': answer.upper()
        }
        
        if device_id:
            payload['device_id'] = device_id
        
        result = await self._request('POST', '/v1/intent', json_data=payload)
        
        logger.info(f"Recommendation response: {answer} - {result}")
        
        # 응답 후 현재 추천 초기화
        if answer.upper() == "YES" or answer.upper() == "NO":
            self.current_recommendation = None
        
        return result
    
    async def get_current_recommendation(self) -> Optional[Dict]:
        """
        현재 대기 중인 추천 가져오기
        
        Returns:
            현재 추천 또는 None
        """
        return self.current_recommendation
    
    async def health_check(self) -> bool:
        """
        AI 서비스 상태 확인
        
        Returns:
            서버가 응답하면 True
        """
        try:
            result = await self._request('GET', '/api/gaze/status', retries=1)
            return result is not None and result.get('status') == 'active'
        except Exception:
            return False
    
    async def get_devices(self) -> Optional[List[Dict]]:
        """
        AI 서비스로부터 디바이스 목록 가져오기 (Gateway에 쿼리)
        
        Returns:
            디바이스 목록 또는 None
        """
        result = await self._request('GET', '/api/devices', params={'user_id': self.user_uuid})
        
        if result and 'devices' in result:
            return result['devices']
        
        return None
    
    async def control_device(self, device_id: str, action: str, 
                           parameters: Optional[Dict] = None) -> Optional[Dict]:
        """
        AI 서비스를 통해 디바이스 제어 명령 전송 (Gateway로 전달)
        
        Args:
            device_id: 디바이스 ID
            action: 수행할 액션
            parameters: 추가 파라미터
            
        Returns:
            제어 결과
        """
        payload = {
            'user_id': self.user_uuid,
            'device_id': device_id,
            'action': action
        }
        
        if parameters:
            payload['parameters'] = parameters
        
        result = await self._request('POST', '/api/devices/control', json_data=payload)
        
        logger.info(f"Device control via AI Service: {device_id} - {action}")
        
        return result
