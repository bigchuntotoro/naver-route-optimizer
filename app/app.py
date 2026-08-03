import os
import sys

# 프로젝트 루트 및 앱 디렉터리를 sys.path에 추가
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
for path in [PROJECT_ROOT, APP_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
from streamlit_folium import st_folium

from config.settings import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
from src.api.directions import NaverDirections
from src.api.geocoder import NaverGeocoder
from src.core.distance_matrix import DistanceMatrixBuilder
from src.core.route_optimizer import RouteOptimizer

from components.map_view import create_route_map

if "page_config_done" not in st.session_state:
    st.set_page_config(page_title="최적 동선 추천 시스템", layout="wide")
    st.session_state.page_config_done = True

st.title("🚗 네이버 지도 기반 최적 동선 추천 시스템")
st.write("방문하고 싶은 장소들의 주소를 입력하면 최소 이동 시간 경로를 추천해 드립니다.")

# API Key 검증
if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    st.error(".env 파일에 NAVER_CLIENT_ID 및 NAVER_CLIENT_SECRET을 설정해 주세요.")
    st.stop()

# 모듈 초기화 (API Key 전달)
geocoder = NaverGeocoder(client_id=NAVER_CLIENT_ID, client_secret=NAVER_CLIENT_SECRET)
directions = NaverDirections(client_id=NAVER_CLIENT_ID, client_secret=NAVER_CLIENT_SECRET)

# 사이드바 입력
st.sidebar.header("📍 장소 입력")
num_places = st.sidebar.number_input(
    "방문 장소 개수",
    min_value=2,
    max_value=7,
    value=2,
    key="num_places_input"
)

input_places = {}
for i in range(int(num_places)):
    default_name = f"출발지" if i == 0 else (f"도착지" if i == num_places - 1 else f"경유지 {i}")
    col1, col2 = st.sidebar.columns([1, 2])
    with col1:
        p_name = st.text_input(
            f"명칭 {i+1}",
            value=default_name,
            key=f"name_input_{i}"
        )
    with col2:
        p_addr = st.text_input(
            f"주소 {i+1}",
            key=f"addr_input_{i}"
        )

    if p_name and p_addr:
        input_places[p_name] = p_addr

# 실행 버튼
if st.sidebar.button("최적 경로 계산하기", key="run_optimizer_button"):
    if len(input_places) < 2:
        st.warning("최소 2개 이상의 주소를 입력해야 합니다.")
    else:
        with st.spinner("주소를 좌표로 변환하고 최적 경로를 계산 중입니다..."):
            # 1. Geocoding
            coords_dict = {}
            failed_places = []
            for name, addr in input_places.items():
                coords = geocoder.geocode(addr)
                # 💡 디버그용: 웹 화면에 변환 결과 바로 출력해보기
                st.write(f"🔍 **[{name}]** '{addr}' -> 좌표 결과: `{coords}`")
                if coords:
                    coords_dict[name] = coords
                else:
                    failed_places.append(name)

            if failed_places:
                st.error(
                    "주소를 찾지 못했습니다. 아래 장소의 주소를 더 정확하게 입력해 주세요: "
                    + ", ".join(failed_places)
                )
                st.info("예: '서울특별시 강남구 테헤란로 427'처럼 도로명과 건물번호를 포함해 입력해 주세요.")
            else:
                # 2. Distance Matrix
                matrix_builder = DistanceMatrixBuilder(directions)
                duration_matrix = matrix_builder.build_matrix(coords_dict)

                # 3. Route Optimization
                place_list = list(coords_dict.keys())
                start_p = place_list[0]
                end_p = place_list[-1]

                optimizer = RouteOptimizer(place_list, duration_matrix)
                best_route, total_time = optimizer.solve(start_place=start_p, end_place=end_p)

                if not best_route:
                    st.error("경로 최적화 결과를 생성하지 못했습니다. 입력한 장소 수나 좌표 정보를 다시 확인해 주세요.")
                else:
                    # 4. 전체 경로의 상세 라인 좌표 받아오기
                    waypoints_coords = [coords_dict[p] for p in best_route[1:-1]]
                    full_route_info = directions.get_route(
                        start=coords_dict[best_route[0]],
                        goal=coords_dict[best_route[-1]],
                        waypoints=waypoints_coords
                    )

                    if full_route_info and full_route_info.get("error"):
                        st.error(full_route_info["error"])
                        if full_route_info.get("details"):
                            st.caption(f"상세 정보: {full_route_info['details']}")
                    else:
                        # 5. 결과 시각화
                        col_res, col_map = st.columns([1, 2])

                        with col_res:
                            st.success("✅ 최적 경로 계산 완료!")
                            st.subheader("📌 추천 순서")
                            for idx, p in enumerate(best_route, 1):
                                st.write(f"**{idx}. {p}**")
                            
                            st.metric("총 예상 이동 시간", f"{total_time} 분")
                            
                            # full_route_info 안전한 검증 후 출력
                            if full_route_info and "distance_km" in full_route_info:
                                st.metric("총 이동 거리", f"{full_route_info['distance_km']} km")

                        with col_map:
                            # 안전하게 path 꺼내기 (KeyError / TypeError 방지)
                            path_coords = full_route_info.get("path", []) if (full_route_info and isinstance(full_route_info, dict)) else []
                            
                            map_obj = create_route_map(coords_dict, best_route, path_coords)
                            st_folium(map_obj, width=700, height=500, returned_objects=[])