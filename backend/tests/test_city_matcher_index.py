"""City DNA matcher: FAISS-backed index with an identical NumPy fallback."""
import numpy as np

from app.data.cities_data import CITIES
from app.services import city_matcher as cm


def test_backend_is_reported_and_valid():
    assert cm.matcher_backend() in ("faiss", "numpy")


def test_results_are_deterministic_and_self_excluding():
    a = [(r["city"]["id"], r["similarity_score"]) for r in cm.find_similar_cities("pune", 5)]
    b = [(r["city"]["id"], r["similarity_score"]) for r in cm.find_similar_cities("pune", 5)]
    assert a == b
    assert all(cid != "pune" for cid, _ in a)        # never returns the target itself
    assert [s for _, s in a] == sorted([s for _, s in a], reverse=True)  # descending


def test_unknown_city_returns_empty():
    assert cm.find_similar_cities("atlantis", 5) == []


class _FakeFaiss:
    """Minimal IndexFlatIP stand-in: exact inner-product search over stored rows,
    so we can exercise the FAISS code path (scatter-back) without the dependency."""

    def __init__(self, rows: np.ndarray):
        self._rows = rows.astype(np.float32)

    def search(self, q: np.ndarray, k: int):
        sims = (self._rows @ q[0]).astype(np.float32)
        order = np.argsort(sims)[::-1][:k]
        return sims[order].reshape(1, -1), order.reshape(1, -1)


def test_faiss_path_matches_numpy_path():
    """Injecting a FAISS-like index must not change the ranking vs the NumPy path."""
    numpy_idx = cm._CityVectorIndex()
    numpy_idx.ensure()

    faiss_idx = cm._CityVectorIndex()
    faiss_idx.ensure()
    faiss_idx._faiss = _FakeFaiss(faiss_idx._normed)  # force the accelerated branch

    target_vec = cm._feature_vector(CITIES["pune"])
    np_res = numpy_idx.query(target_vec, exclude_id="pune", top_n=8)
    fa_res = faiss_idx.query(target_vec, exclude_id="pune", top_n=8)
    assert [c for c, _ in np_res] == [c for c, _ in fa_res]


def test_system_metrics_exposes_matcher_backend():
    from fastapi.testclient import TestClient

    from app.main import app

    snap = TestClient(app).get("/api/system/metrics").json()
    assert snap["city_matcher_backend"] in ("faiss", "numpy")
