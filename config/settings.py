import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 네이버 Cloud API Key (환경 변수에서 불러오기)
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "")

# API Key 로드 검증 (개발 편의용)
if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    print("⚠️ 경고: NAVER API Key가 .env 파일에서 정상적으로 로드되지 않았습니다.")

# API Endpoint URLs
GEOCODE_URL = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
DIRECTIONS_URL = "https://maps.apigw.ntruss.com/map-direction-15/v1/driving"