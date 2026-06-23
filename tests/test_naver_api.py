import pytest
from unittest.mock import patch, MagicMock
from naver_api import search_places

def test_search_places_returns_list():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {"title": "스타벅스 연남점", "address": "서울시 마포구", "category": "카페"},
            {"title": "블루보틀 연남", "address": "서울시 마포구", "category": "카페"},
        ]
    }
    with patch("naver_api.requests.get", return_value=mock_response):
        result = search_places("연남동 카페", client_id="test_id", client_secret="test_secret")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["title"] == "스타벅스 연남점"

def test_search_places_empty_result():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"items": []}
    with patch("naver_api.requests.get", return_value=mock_response):
        result = search_places("없는동네 우주음식점", client_id="test_id", client_secret="test_secret")
    assert result == []

def test_search_places_api_error():
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = Exception("Unauthorized")
    with patch("naver_api.requests.get", return_value=mock_response):
        with pytest.raises(Exception):
            search_places("연남동 카페", client_id="bad_id", client_secret="bad_secret")
