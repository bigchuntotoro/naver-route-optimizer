import folium
from typing import List, Tuple, Dict


def create_route_map(
    places_coords: Dict[str, Tuple[float, float]], 
    optimal_route: List[str], 
    path_coords: List[List[float]]
) -> folium.Map:
    """
    최적 경로 및 마커가 표시된 Folium 지도를 생성합니다.
    """
    # 첫 장소 중심으로 지도 초기화 (위도, 경도)
    start_place = optimal_route[0]
    start_lng, start_lat = places_coords[start_place]
    
    m = folium.Map(location=[start_lat, start_lng], zoom_start=12)

    # 1. 경로 선 그리기 (Folium은 [위도, 경도] 순서 필요)
    if path_coords:
        folium_path = [[lat, lng] for lng, lat in path_coords]
        folium.PolyLine(
            locations=folium_path,
            color="blue",
            weight=5,
            opacity=0.7
        ).add_to(m)

    # 2. 장소별 마커 표시
    for idx, place in enumerate(optimal_route, 1):
        lng, lat = places_coords[place]
        
        # 출발지, 도착지, 경유지 마커 색상 구분
        if idx == 1:
            color = "red"
            icon_name = "play"
        elif idx == len(optimal_route):
            color = "black"
            icon_name = "flag"
        else:
            color = "blue"
            icon_name = "info-sign"

        folium.Marker(
            location=[lat, lng],
            popup=f"<b>{idx}. {place}</b>",
            tooltip=f"{idx}. {place}",
            icon=folium.Icon(color=color, icon=icon_name)
        ).add_to(m)

    return m