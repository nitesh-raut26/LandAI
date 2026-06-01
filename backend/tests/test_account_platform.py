"""Persistent product platform: watchlist, compare history, saved searches,
and the User / API-usage dashboards."""
import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _auth():
    email = f"p{uuid.uuid4().hex[:10]}@example.com"
    tok = client.post("/api/auth/register", json={"email": email, "password": "supersecret1"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


# ── watchlist ────────────────────────────────────────────────────────────────
def test_watchlist_crud_and_idempotent():
    h = _auth()
    assert client.get("/api/account/watchlist", headers=h).json() == []
    assert client.post("/api/account/watchlist", json={"city_id": "pune"}, headers=h).status_code == 201
    # second add of the same city must not create a duplicate (merge-safe sync)
    client.post("/api/account/watchlist", json={"city_id": "pune"}, headers=h)
    lst = client.get("/api/account/watchlist", headers=h).json()
    assert [w["city_id"] for w in lst] == ["pune"]
    assert client.delete("/api/account/watchlist/pune", headers=h).status_code == 200
    assert client.get("/api/account/watchlist", headers=h).json() == []
    assert client.delete("/api/account/watchlist/pune", headers=h).status_code == 404


def test_watchlist_requires_auth():
    assert client.get("/api/account/watchlist").status_code == 401
    assert client.post("/api/account/watchlist", json={"city_id": "pune"}).status_code == 401


# ── compare history ──────────────────────────────────────────────────────────
def test_compare_history_records_and_dedupes():
    h = _auth()
    r = client.post("/api/account/compare-history", json={"city_a": "pune", "city_b": "nagpur"}, headers=h)
    assert r.status_code == 201
    first_id = r.json()["id"]
    # immediate duplicate of the same pair (reversed) collapses, no new row
    dup = client.post("/api/account/compare-history", json={"city_a": "nagpur", "city_b": "pune"}, headers=h)
    assert dup.json()["id"] == first_id
    client.post("/api/account/compare-history", json={"city_a": "pune", "city_b": "indore"}, headers=h)
    hist = client.get("/api/account/compare-history", headers=h).json()
    assert len(hist) == 2  # newest first
    assert hist[0]["city_b"] == "indore"
    assert client.delete(f"/api/account/compare-history/{first_id}", headers=h).status_code == 200


# ── saved searches ───────────────────────────────────────────────────────────
def test_saved_searches_persist_and_filter_query():
    h = _auth()
    r = client.post(
        "/api/account/saved-searches",
        json={"label": "MH Tier-1", "query": {"q": "", "state": "Maharashtra", "tier": 1, "junk": "drop-me"}},
        headers=h,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["query"] == {"state": "Maharashtra", "tier": 1}  # empty + unknown keys stripped
    assert body["label"] == "MH Tier-1"
    lst = client.get("/api/account/saved-searches", headers=h).json()
    assert len(lst) == 1
    assert client.delete(f"/api/account/saved-searches/{body['id']}", headers=h).status_code == 200
    assert client.get("/api/account/saved-searches", headers=h).json() == []


# ── dashboard ────────────────────────────────────────────────────────────────
def test_dashboard_aggregates_counts():
    h = _auth()
    client.post("/api/account/watchlist", json={"city_id": "pune"}, headers=h)
    client.post("/api/account/saved-cities", json={"city_id": "nagpur", "note": "x"}, headers=h)
    client.post("/api/account/compare-history", json={"city_a": "pune", "city_b": "nagpur"}, headers=h)
    d = client.get("/api/account/dashboard", headers=h).json()
    assert d["tier"] == "developer"
    assert d["counts"]["watchlist"] == 1
    assert d["counts"]["saved_cities"] == 1
    assert d["counts"]["compares"] == 1
    assert d["watchlist"] == ["pune"]
    assert len(d["recent_compares"]) == 1


# ── usage history (real usage_logs aggregation) ──────────────────────────────
def test_usage_history_empty_then_reflects_metered_calls():
    h = _auth()
    empty = client.get("/api/account/usage-history", headers=h).json()
    assert empty["total_requests"] == 0
    assert len(empty["series"]) == 30  # zero-filled day series
    assert empty["by_endpoint"] == []

    key = client.post("/api/keys", json={"name": "ci"}, headers=h).json()["api_key"]
    for _ in range(3):
        assert client.get("/api/v1/city/pune", headers={"X-API-Key": key}).status_code == 200

    hist = client.get("/api/account/usage-history", headers=h).json()
    assert hist["total_requests"] == 3
    assert hist["by_endpoint"][0]["count"] == 3
    assert hist["by_status"]["200"] == 3
    assert hist["by_key"][0]["count"] == 3


def test_usage_history_requires_auth():
    assert client.get("/api/account/usage-history").status_code == 401
    assert client.get("/api/account/dashboard").status_code == 401
