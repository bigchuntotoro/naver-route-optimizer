from src.api.geocoder import NaverGeocoder


def test_build_candidate_queries_returns_fallback_variants():
    geocoder = NaverGeocoder("test-id", "test-secret")

    candidates = geocoder._build_candidate_queries("서울특별시 강남구 테헤란로 427")

    assert candidates[0] == "서울특별시 강남구 테헤란로 427"
    assert "서울특별시 강남구 테헤란로" in candidates
    assert "서울특별시 강남구" in candidates
