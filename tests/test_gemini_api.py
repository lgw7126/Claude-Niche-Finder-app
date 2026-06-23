import pytest
from unittest.mock import patch, MagicMock
from gemini_api import analyze_market

SAMPLE_PLACES = [
    {"title": "스타벅스 연남점", "address": "서울시 마포구 연남동", "category": "카페"},
    {"title": "블루보틀 연남", "address": "서울시 마포구 연남동", "category": "카페"},
    {"title": "이디야 연남점", "address": "서울시 마포구 연남동", "category": "카페"},
]

def test_analyze_market_returns_string():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "경쟁 강도 높음. 프리미엄 포지셔닝 추천."
    mock_client.models.generate_content.return_value = mock_response
    with patch("gemini_api.genai.Client", return_value=mock_client):
        result = analyze_market(SAMPLE_PLACES, query="연남동 카페", api_key="test_key")
    assert isinstance(result, str)
    assert len(result) > 0

def test_analyze_market_empty_places():
    with pytest.raises(ValueError, match="매장 데이터가 없습니다"):
        analyze_market([], query="연남동 카페", api_key="test_key")
