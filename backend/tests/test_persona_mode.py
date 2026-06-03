"""Investor Persona Mode (Vision §3.5): same signals, re-weighted per buyer."""
from fastapi.testclient import TestClient

from app.data.cities_data import get_all_cities
from app.main import app
from app.services.scoring import PERSONAS, compute_score, normalize_persona

client = TestClient(app)
_CITY = get_all_cities()[0]["id"]


def test_all_persona_weights_sum_to_one():
    for key, p in PERSONAS.items():
        assert abs(sum(p["weights"].values()) - 1.0) < 1e-9, key


def test_balanced_is_the_default_and_unchanged_shape():
    city = get_all_cities()[0]
    base = compute_score(city)
    assert base["persona"] == "balanced"
    # default == explicit balanced == an unknown persona (falls back to balanced)
    assert base["composite_score"] == compute_score(city, "balanced")["composite_score"]
    assert base["composite_score"] == compute_score(city, "weird-input")["composite_score"]
    assert normalize_persona("WEIRD") == "balanced"


def test_personas_reweight_the_composite():
    city = get_all_cities()[0]
    scores = {k: compute_score(city, k)["composite_score"] for k in PERSONAS}
    # The persona lens must actually move the number for at least one persona.
    assert len({round(v, 1) for v in scores.values()}) > 1
    # And every call exposes the full spread so the UI needs only one request.
    assert compute_score(city)["persona_scores"].keys() == PERSONAS.keys()


def test_endpoint_accepts_persona_and_lists_catalogue():
    cat = client.get("/api/score/personas").json()
    keys = {p["key"] for p in cat["personas"]}
    assert {"balanced", "small", "builder", "nri"} <= keys

    r = client.get(f"/api/score/{_CITY}", params={"persona": "builder"})
    assert r.status_code == 200
    body = r.json()
    assert body["persona"] == "builder"
    assert body["persona_label"] == "Builder / Developer"
    assert "persona_fit" in body
