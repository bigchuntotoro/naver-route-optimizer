import re
import requests
from typing import Optional, Tuple, List
from config.settings import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, GEOCODE_URL


class NaverGeocoder:
    """네이버 Geocoding API 연동 클래스 (검색 성공률 향상 로직 포함)"""

    def __init__(self, client_id: str = NAVER_CLIENT_ID, client_secret: str = NAVER_CLIENT_SECRET):
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret
        }

    def _request_geocode(self, query_str: str) -> Optional[Tuple[float, float]]:
        params = {"query": query_str}
        try:
            response = requests.get(GEOCODE_URL, headers=self.headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                addresses = data.get("addresses", [])
                if addresses:
                    target_addr = addresses[0]
                    for addr_info in addresses:
                        if addr_info.get("roadAddress"):
                            target_addr = addr_info
                            break
                    
                    lng = float(target_addr["x"])
                    lat = float(target_addr["y"])
                    return (lng, lat)
            return None
        except Exception as e:
            print(f"[Geocode Error] '{query_str}' 변환 중 예외 발생: {e}", flush=True)
            return None

    def _normalize_address(self, address: str) -> str:
        """주소의 줄임말 정제 및 도로명/숫자 붙여쓰기 교정"""
        addr = address.strip()

        # 1. 시/도 줄임말을 정식 행정구역명으로 변환
        city_replacements = {
            r"^서울\s": "서울특별시 ",
            r"^경기\s": "경기도 ",
            r"^인천\s": "인천광역시 ",
            r"^부산\s": "부산광역시 ",
            r"^대구\s": "대구광역시 ",
            r"^광주\s": "광주광역시 ",
            r"^대전\s": "대전광역시 ",
            r"^울산\s": "울산광역시 ",
            r"^세종\s": "세종특별자치시 ",
            r"^강원\s": "강원특별자치도 ",
            r"^충북\s": "충청북도 ",
            r"^충남\s": "충청남도 ",
            r"^전북\s": "전북특별자치도 ",
            r"^전남\s": "전라남도 ",
            r"^경북\s": "경상북도 ",
            r"^경남\s": "경상남도 ",
            r"^제주\s": "제주특별자치도 "
        }

        for pattern, replacement in city_replacements.items():
            addr = re.sub(pattern, replacement, addr)

        # 2. '곰달래로 2길'처럼 도로명과 숫자길 사이의 띄어쓰기를 붙여주는 교정 ('곰달래로2길')
        addr = re.sub(r'([가-힣]+(?:대로|로))\s+(\d+길)', r'\1\2', addr)

        return addr

    def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        if not address or not address.strip():
            return None

        # [1차 시도] 원본 입력 주소로 검색
        result = self._request_geocode(address)
        if result:
            return result

        # [2차 시도] 정규화된 주소(띄어쓰기 붙이기 적용)로 검색
        normalized_addr = self._normalize_address(address)
        if normalized_addr != address:
            result = self._request_geocode(normalized_addr)
            if result:
                return result

        # [3차 시도] '곰달래로 2길' 형태에서 공백 제거 처리 시도
        no_space_street = re.sub(r'([가-힣]+(?:대로|로))\s+(\d+)', r'\1\2', address)
        if no_space_street != address:
            result = self._request_geocode(no_space_street)
            if result:
                return result

        # [4차 시도] 건물 번호 제거 후 도로명까지만 검색
        tokens = normalized_addr.split()
        if len(tokens) > 2:
            short_addr = " ".join(tokens[:-1])
            result = self._request_geocode(short_addr)
            if result:
                return result

        return None