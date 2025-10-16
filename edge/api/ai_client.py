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
    """Client for AI Service API"""
    
    def __init__(self, base_url: str, user_uuid: str):
        self.base_url = base_url.rstrip('/')
        self.user_uuid = user_uuid
        self.session: Optional[aiohttp.ClientSession] = None
        self.current_recommendation: Optional[Dict] = None
        
        logger.info(f"AIServiceClient initialized: {base_url}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _request(self, method: str, endpoint: str, 
                      json_data: Optional[Dict] = None,
                      params: Optional[Dict] = None,
                      retries: int = 3) -> Optional[Dict]:
        """
        Make HTTP request with retries
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            json_data: JSON payload
            params: Query parameters
            retries: Number of retries
            
        Returns:
            Response data or None on error
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
        Send device click event to AI service for recommendation
        
        Args:
            device_info: Clicked device information
            context: Additional context
            
        Returns:
            Recommendation from AI service
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
            # Add recommendation_id from response if available
            if 'recommendation_id' not in self.current_recommendation and 'session_id' in result:
                self.current_recommendation['recommendation_id'] = result['session_id']
            
            logger.info(f"Received recommendation: {self.current_recommendation.get('prompt_text', '')[:50]}...")
        
        return result
    
    async def poll_recommendation(self) -> Optional[Dict]:
        """
        Poll for pending recommendations
        
        Returns:
            Recommendation if available
        """
        params = {'user_uuid': self.user_uuid}
        result = await self._request('GET', '/v1/intent', params=params, retries=1)
        
        if result and result.get('status') == 'success':
            # Check if there's a pending recommendation
            if 'recommendation' in result:
                self.current_recommendation = result['recommendation']
                logger.info(f"Polled recommendation: {self.current_recommendation.get('message', '')[:50]}...")
                return self.current_recommendation
        
        return None
    
    async def respond_to_recommendation(self, recommendation_id: str, answer: str, 
                                       device_id: Optional[str] = None) -> Optional[Dict]:
        """
        Send YES/NO response to a recommendation
        
        Args:
            recommendation_id: ID of the recommendation
            answer: "YES" or "NO"
            device_id: Device ID (if applicable)
            
        Returns:
            Response result
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
        
        # Clear current recommendation after responding
        if answer.upper() == "YES" or answer.upper() == "NO":
            self.current_recommendation = None
        
        return result
    
    async def get_current_recommendation(self) -> Optional[Dict]:
        """
        Get the current pending recommendation
        
        Returns:
            Current recommendation or None
        """
        return self.current_recommendation
    
    async def health_check(self) -> bool:
        """
        Check if AI service is healthy
        
        Returns:
            True if server is responding
        """
        try:
            result = await self._request('GET', '/api/gaze/status', retries=1)
            return result is not None and result.get('status') == 'active'
        except Exception:
            return False
    
    async def get_devices(self) -> Optional[List[Dict]]:
        """
        Get device list from AI Service (which queries Gateway)
        
        Returns:
            List of devices or None
        """
        result = await self._request('GET', '/api/devices', params={'user_id': self.user_uuid})
        
        if result and 'devices' in result:
            return result['devices']
        
        return None
    
    async def control_device(self, device_id: str, action: str, 
                           parameters: Optional[Dict] = None) -> Optional[Dict]:
        """
        Send device control command via AI Service (which forwards to Gateway)
        
        Args:
            device_id: Device ID
            action: Action to perform
            parameters: Additional parameters
            
        Returns:
            Control result
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
