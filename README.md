🗺️ naver-route-optimizer

네이버 지도 API 기반 최적 이동 경로 추천 시스템

Python + Streamlit + Naver Maps API를 활용하여 여러 장소의 주소를 입력하면
각 장소 간 이동 시간/거리를 계산하고, 최소 이동 시간 기준의 최적 방문 순서를 추천하는 프로젝트입니다.

🏗️ 전체 프로젝트 디렉토리 구조

```text
naver-route-optimizer/
│
├── config/                     # 설정 파일 및 환경변수
│   ├── __init__.py
│   └── settings.py             # API Key, 상수, 기본 설정 관리
│
├── data/                       # 데이터 저장소 (옵션)
│   ├── sample_places.json      # 샘플 장소 및 좌표 데이터
│   └── cache/                  # API 호출 최소화를 위한 캐시 폴더
│
├── src/                        # 핵심 로직 소스코드
│   ├── __init__.py
│   ├── api/                    # 외부 API 연동 모듈
│   │   ├── __init__.py
│   │   ├── geocoder.py         # 주소 ↔ 좌표 변환 (Geocoding API)
│   │   └── directions.py       # 이동시간/거리 계산 (Directions API)
│   │
│   ├── core/                   # 핵심 알고리즘 및 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── distance_matrix.py  # N개 장소 간 이동시간 행렬(Matrix) 생성
│   │   └── route_optimizer.py # 최적 동선 계산 (TSP / Permutations)
│   │
│   └── utils/                  # 공통 유틸리티
│       ├── __init__.py
│       └── helpers.py          # 좌표 포맷 변환, 시간 단위 변환 등
│
├── app/                        # 사용자 인터페이스 (Web UI)
│   ├── app.py                  # Streamlit / Flask 메인 앱 실행 파일
│   └── components/             # 지도 시각화 및 UI 컴포넌트
│       └── map_view.py         # Folium / Pydeck 지도 마커 & 경로 시각화
│
├── .env                        # 네이버 API Key 등 보안 정보 (git 미포함)
├── .gitignore
├── requirements.txt            # 필요 패키지 목록 (requests, streamlit, folium 등)
└── README.md                   # 프로젝트 설명서
```

🧩 모듈별 역할 및 데이터 흐름

```text
[ 사용자 입력 ] (주소 또는 장소 목록)
       │
       ▼
┌─────────────────────────────────────────┐
│ 1. Geocoding 모듈 (src/api/geocoder.py)  │ ──> 주소를 (경도, 위도) 좌표로 변환
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ 2. Matrix 생성 모듈 (src/core/distance_... )│ ──> Directions API (src/api/directions.py) 반복 호출
└─────────────────────────────────────────────┘     장소 간 N x N 이동시간 행렬 구축
       │
       ▼
┌─────────────────────────────────────────────┐
│ 3. 최적화 알고리즘 (src/core/route_opti... ) │ ──> 최소 이동시간 조합/순서 산출
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ 4. 시각화 & UI (app/app.py & map_view.py)   │ ──> Folium 지도로 최적 경로 마커/선 시각화
└─────────────────────────────────────────────┘
```

🛠️ 개발 환경
Language
Python 3.12+
Framework
Streamlit
API
Naver Cloud Platform Maps API

사용 API:

Geocoding API
Directions API
Library
requests
streamlit
folium
streamlit-folium
python-dotenv

서버기동

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/app.py
```
