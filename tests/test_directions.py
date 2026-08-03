from src.api.directions import NaverDirections


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text or ""

    def json(self):
        return self._payload


def test_get_route_falls_back_to_v1_when_v5_returns_404(monkeypatch):
    calls = []
    responses = [
        FakeResponse(status_code=404, payload={}),
        FakeResponse(
            status_code=200,
            payload={
                "code": 0,
                "route": {
                    "trafast": [
                        {
                            "summary": {"duration": 60000, "distance": 1000},
                            "path": [[127.0, 37.0], [127.1, 37.1]],
                        }
                    ]
                },
            },
        ),
    ]

    def fake_get(url, headers=None, params=None, timeout=5):
        calls.append((url, params))
        return responses.pop(0)

    monkeypatch.setattr("src.api.directions.requests.get", fake_get)

    directions = NaverDirections("client-id", "client-secret")
    result = directions.get_route((127.0, 37.0), (127.1, 37.1))

    assert result is not None
    assert result["distance_km"] == 1.0
    assert len(calls) == 2
    assert calls[1][0].endswith("/v1/driving")


def test_get_route_explains_subscription_required_for_401(monkeypatch):
    def fake_get(url, headers=None, params=None, timeout=5):
        return FakeResponse(status_code=401, payload={"message": "Permission Denied"})

    monkeypatch.setattr("src.api.directions.requests.get", fake_get)

    directions = NaverDirections("client-id", "client-secret")
    result = directions.get_route((127.0, 37.0), (127.1, 37.1))

    assert result["error"].startswith("네이버 Directions API 권한이 없습니다")
    assert "구독 상태" in result["error"]
