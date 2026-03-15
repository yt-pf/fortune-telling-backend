import pytest
from fastapi.testclient import TestClient

from api import app

# テストクライアントのセットアップ
client = TestClient(app)


class TestPillarsEndpoint:
    """
    /pillars エンドポイントの単体テスト
    """

    def test_get_pillars_with_hour(self):
        """有効な日付と時間で四柱推命データを取得できるか"""
        response = client.get(
            "/pillars", params={"y": 1990, "m": 5, "d": 15, "h": 14, "g": 1}
        )

        assert response.status_code == 200
        data = response.json()

        # 必須フィールドが存在するか確認
        assert "year_stem" in data
        assert "year_branch" in data
        assert "day_stem" in data
        assert "hour_stem" in data  # 時間が指定されているため "-" ではないはず

        # 時間が指定されている場合、時間関連のフィールドが "-" でないことを簡易チェック
        assert data["hour_stem"] != "－"
        assert data["hour_branch"] != "－"

    def test_get_pillars_without_hour(self):
        """時間を指定しない場合、時間関連のフィールドが "-" になるか"""
        response = client.get("/pillars", params={"y": 1990, "m": 5, "d": 15, "g": 0})

        assert response.status_code == 200
        data = response.json()

        assert data["hour_stem"] == "－"
        assert data["hour_branch"] == "－"
        assert data["hour_hidden_stems"] == "－"

    def test_get_pillars_missing_required_params(self):
        """必須パラメータ (y, m, d) が欠落している場合、422 エラーを返すか"""
        response = client.get("/pillars", params={"y": 1990})  # m, d 欠落

        assert response.status_code == 422
        assert "detail" in response.json()
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert len(detail) > 0
            assert any("m" in str(d) or "d" in str(d) for d in detail)
        else:
            assert "required" in str(detail).lower()

    def test_get_pillars_invalid_hour(self):
        """時間が 0-23 の範囲外の場合、400 エラーを返すか"""
        response = client.get("/pillars", params={"y": 1990, "m": 5, "d": 15, "h": 25})

        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Invalid hour" in response.json()["detail"]

    def test_get_pillars_invalid_date(self):
        """存在しない日付 (例: 2月30日) を指定した場合、400 エラーを返すか"""
        response = client.get("/pillars", params={"y": 2023, "m": 2, "d": 30})

        assert response.status_code == 400
        assert "detail" in response.json()
        assert "Invalid date" in response.json()["detail"]


class TestNumerologyEndpoint:
    """
    /numerology エンドポイントの単体テスト
    """

    def test_get_numerology(self):
        """有効な日付で数秘術データを取得できるか"""
        response = client.get("/numerology", params={"y": 1990, "m": 5, "d": 15})

        assert response.status_code == 200
        data = response.json()

        assert "life_path_number" in data
        assert "past_number" in data
        assert "future_number" in data

        # 数値が整数であることを確認
        assert isinstance(data["life_path_number"], int)
        assert isinstance(data["past_number"], int)
        assert isinstance(data["future_number"], int)

    def test_get_numerology_missing_params(self):
        """必須パラメータが欠落している場合、422 エラーを返すか"""
        response = client.get("/numerology", params={"y": 1990})

        assert response.status_code == 422
        assert "detail" in response.json()
        # FastAPI の 422 エラーは detail がリスト形式になることが多い
        detail = response.json()["detail"]
        if isinstance(detail, list):
            assert len(detail) > 0
            assert any("m" in str(d) or "d" in str(d) for d in detail)
        else:
            assert "required" in str(detail).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
