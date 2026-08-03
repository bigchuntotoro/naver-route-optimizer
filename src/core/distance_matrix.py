from typing import Dict, List, Tuple, Any
from src.api.directions import NaverDirections


class DistanceMatrixBuilder:
    """여러 장소 간의 N x N 이동 시간/거리 행렬을 구축하는 클래스"""

    def __init__(self, directions_api: NaverDirections):
        self.directions_api = directions_api

    def build_matrix(
        self, 
        places_data: Dict[str, Tuple[float, float]]
    ) -> Dict[Tuple[str, str], float]:
        """
        장소 목록과 각 장소의 좌표를 받아 모든 쌍(Pair) 간의 이동시간 행렬을 만듭니다.

        :param places_data: {"장소명": (경도, 위도)} 형태의 딕셔너리
        :return: {("출발장소", "도착장소"): 이동시간(분)} 형태의 행렬 딕셔너리
        """
        matrix = {}
        place_names = list(places_data.keys())

        for origin in place_names:
            for destination in place_names:
                # 자기 자신으로의 이동은 0분
                if origin == destination:
                    matrix[(origin, destination)] = 0.0
                    continue

                start_coords = places_data[origin]
                goal_coords = places_data[destination]

                # Directions API 호출
                route_info = self.directions_api.get_route(start_coords, goal_coords)

                # 💡 안전한 Key 접근 및 에러 검증
                print("ROUTE_INFO =", route_info)
                if isinstance(route_info, dict) and "error" not in route_info:
                    # 'duration_min' 우선 확인 후 없으면 'duration' 확인
                    duration = route_info.get("duration_min", route_info.get("duration"))
                    
                    if duration is not None:
                        matrix[(origin, destination)] = float(duration)
                    else:
                        print(f"[DistanceMatrix Warning] '{origin}' -> '{destination}' 경로에 duration 키가 없음: {route_info}", flush=True)
                        matrix[(origin, destination)] = float("inf")
                else:
                    # 호출 실패 시 또는 에러 메시지가 반환된 경우 무한대 부여
                    print(f"[DistanceMatrix Error] '{origin}' -> '{destination}' 경로 호출 실패: {route_info}", flush=True)
                    matrix[(origin, destination)] = float("inf")

        return matrix