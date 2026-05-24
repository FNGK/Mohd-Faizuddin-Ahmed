from fastapi.testclient import TestClient

from app.main import app
from app.seed import run_seed

client = TestClient(app)


def setup_module():
    run_seed()


def test_health():
    for path in ("/api/health", "/api/v1/health"):
        res = client.get(path)
        assert res.status_code == 200
        assert res.json()["cms"] is True


def test_login_and_me():
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@seowithfaiz.com", "password": "ChangeThisBeforeDeploy123!"},
    )
    assert res.status_code == 200
    tokens = res.json()
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["role"] == "superadmin"


def test_public_contact_honeypot():
    res = client.post(
        "/api/v1/contact",
        json={
            "name": "Bot",
            "email": "bot@test.com",
            "website": "https://example.com",
            "region": "USA",
            "goal": "This should be ignored by honeypot.",
            "honeypot": "spam",
        },
    )
    assert res.status_code == 201
    assert res.json()["success"] is True
