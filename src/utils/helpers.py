from typing import Tuple, List, Union, Dict, Any


def is_valid_coordinates(lng: float, lat: float) -> bool:
    """
    경도(Longitude)와 위도(Latitude)가 대한민국 영역 내의 유효한 범위를 가지는지 검증합니다.
    
    :param lng: 경도 (X 좌표)
    :param lat: 위도 (Y 좌표)
    :return: 유효 범위 내에 있으면 True, 아니면 False
    """
    # 대한민국 대략적 경위도 범위 (경도 124~132, 위도 33~39)
    is_valid_lng = 124.0 <= lng <= 132.0
    is_valid_lat = 33.0 <= lat <= 39.0
    return is_valid_lng and is_valid_lat


def format_duration(minutes: Union[int, float]) -> str:
    """
    분(Minutes) 단위의 소요 시간을 보기 좋은 한국어 문자열로 변환합니다.
    
    예시: 
    - 45.0 -> "45분"
    - 135.5 -> "2시간 16분"
    """
    total_minutes = round(minutes)
    if total_minutes < 60:
        return f"{total_minutes}분"
    
    hours = total_minutes // 60
    remaining_mins = total_minutes % 60
    
    if remaining_mins == 0:
        return f"{hours}시간"
    return f"{hours}시간 {remaining_mins}분"


def format_distance(meters: Union[int, float]) -> str:
    """
    미터(Meters) 단위의 거리를 km 또는 m 문자열로 보기 좋게 포맷팅합니다.
    
    예시:
    - 850 -> "850m"
    - 14200 -> "14.2km"
    """
    if meters < 1000:
        return f"{int(meters)}m"
    km = round(meters / 1000, 1)
    return f"{km}km"


def convert_path_to_folium_coords(path: List[List[float]]) -> List[Tuple[float, float]]:
    """
    네이버 API 경로 좌표([[경도, 위도], ...])를 
    Folium 지도용 좌표([[위도, 경도], ...]) 형태 포맷으로 반환합니다.
    
    :param path: 네이버 API 반환 좌표 리스트 [[lng, lat], [lng, lat], ...]
    :return: Folium용 좌표 리스트 [(lat, lng), (lat, lng), ...]
    """
    return [(lat, lng) for lng, lat in path]


def parse_address_string(raw_text: str) -> List[Dict[str, str]]:
    """
    사용자가 줄바꿈(Enter)으로 여러 주소를 한 번에 입력했을 때
    이를 한 줄씩 파싱하여 dict 리스트로 반환합니다.
    
    예시 입력:
    "서울역, 서울 용산구 한강대로 405\n경복궁, 서울 종로구 사직로 161"
    
    :return: [{'name': '서울역', 'address': '서울 용산구 한강대로 405'}, ...]
    """
    parsed_items = []
    lines = raw_text.strip().split("\n")
    
    for idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        if "," in line:
            parts = line.split(",", 1)
            name = parts[0].strip()
            address = parts[1].strip()
        else:
            name = f"장소 {idx}"
            address = line
            
        parsed_items.append({"name": name, "address": address})
        
    return parsed_items


# 파일 단독 실행 시 유틸리티 함수 기능 테스트
if __name__ == "__main__":
    print("=== helpers.py 단독 테스트 ===")
    
    # 1. 시간 변환 테스트
    print(f"75.4분 변환: {format_duration(75.4)}")  # 1시간 15분
    
    # 2. 거리 변환 테스트
    print(f"12400m 변환: {format_distance(12400)}")  # 12.4km
    
    # 3. 좌표 유효성 검증
    print(f"서울역 좌표(126.97, 37.55) 유효성: {is_valid_coordinates(126.97, 37.55)}")  # True
    
    # 4. 좌표 뒤집기(Folium 변환) 테스트
    sample_path = [[127.10, 37.35], [127.02, 37.49]]
    print(f"Folium 좌표 변환: {convert_path_to_folium_coords(sample_path)}")