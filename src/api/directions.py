import requests
from typing import Optional, Dict, Any, Tuple, List


class NaverDirections:
    """네이버 Directions API 연동 클래스"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        # Directions 15 및 Fallback(Directions 5) 엔드포인트
        self.urls = [
            "https://maps.apigw.ntruss.com/map-direction-15/v1/driving"
        ]
        self.headers = {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret
        }

    def _extract_error_detail(self, response) -> str:
        try:
            payload = response.json()
        except Exception:
            payload = {}

        if isinstance(payload, dict):
            if isinstance(payload.get("error"), dict):
                nested_error = payload["error"]
                return nested_error.get("message") or nested_error.get("errorCode") or response.text
            return payload.get("message") or payload.get("error") or response.text

        return response.text

    def get_route(self, start, goal, waypoints=None, option="trafast"):
        params = {
            "start": f"{start[0]},{start[1]}",
            "goal": f"{goal[0]},{goal[1]}",
            "option": option
        }
        if waypoints:
            params["waypoints"] = "|".join([f"{wp[0]},{wp[1]}" for wp in waypoints])

        errors = {}
        for url in self.urls:
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=5)
                print(f"[{url}] status={response.status_code} body={response.text[:300]}")  # 확인용
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        route_data = data["route"][option][0]
                        summary = route_data["summary"]
                        return {
                            "duration_min": round(summary["duration"] / (1000 * 60), 1),
                            "distance_km": round(summary["distance"] / 1000, 2),
                            "toll_fare": summary.get("tollFare", 0),
                            "path": route_data["path"],
                        }
                    errors[url] = data.get("message", "unknown business error")
                elif response.status_code in [401, 403]:
                    detail = self._extract_error_detail(response)
                    errors[url] = f"HTTP {response.status_code} ({detail})"
                    return {
                        "error": "네이버 Directions API 권한이 없습니다. 네이버 Cloud Console에서 Directions API 구독 상태와 API 키를 확인해 주세요.",
                        "details": errors,
                    }
                else:
                    errors[url] = f"HTTP {response.status_code} ({response.text})"
                    if response.status_code != 404:
                        break
            except Exception as e:
                errors[url] = str(e)

        return {"error": "네이버 Directions API 호출 실패", "details": errors}