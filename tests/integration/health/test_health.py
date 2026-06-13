import pytest

pytestmark = pytest.mark.integration


class TestLiveness:
    async def test_live_returns_200(self, client):
        response = await client.get("/health/live")
        assert response.status_code == 200

    async def test_live_returns_ok_status(self, client):
        response = await client.get("/health/live")
        assert response.json() == {"status": "ok"}


class TestReadiness:
    async def test_ready_returns_status_field(self, client):
        response = await client.get("/health/ready")
        data = response.json()
        assert "status" in data
        assert data["status"] in ("ok", "degraded", "down")

    async def test_ready_returns_checks_field(self, client):
        response = await client.get("/health/ready")
        data = response.json()
        assert "checks" in data
        assert "db" in data["checks"]
        assert "redis" in data["checks"]

    async def test_ready_check_has_status(self, client):
        response = await client.get("/health/ready")
        checks = response.json()["checks"]
        for check in checks.values():
            assert "status" in check

    async def test_ready_db_is_ok(self, client):
        response = await client.get("/health/ready")
        db_check = response.json()["checks"]["db"]
        assert db_check["status"] == "ok"
        assert "latency_ms" in db_check

    async def test_ready_http_200_when_ok(self, client):
        response = await client.get("/health/ready")
        data = response.json()
        if data["status"] == "ok":
            assert response.status_code == 200

    async def test_ready_http_503_when_not_ok(self, client):
        response = await client.get("/health/ready")
        data = response.json()
        if data["status"] in ("degraded", "down"):
            assert response.status_code == 503


class TestHealth:
    async def test_health_returns_detailed_response(self, client):
        response = await client.get("/health")
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "db" in data["checks"]
        assert "redis" in data["checks"]

    async def test_health_db_ok_with_latency(self, client):
        response = await client.get("/health")
        db_check = response.json()["checks"]["db"]
        assert db_check["status"] == "ok"
        assert isinstance(db_check["latency_ms"], float)

    async def test_health_status_matches_ready(self, client):
        health_resp = await client.get("/health")
        ready_resp = await client.get("/health/ready")
        assert health_resp.json()["status"] == ready_resp.json()["status"]
        assert health_resp.status_code == ready_resp.status_code
