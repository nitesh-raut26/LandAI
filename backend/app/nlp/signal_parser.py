"""
Infrastructure Signal NLP
=========================
Classical NLP pipeline that turns free-text infrastructure announcements into
structured, scored *leading indicators* of land-value change.

What is real here
-----------------
- TF-IDF vectorisation (scikit-learn) of the announcement corpus, used both for
  global term statistics and for city <-> document retrieval via cosine
  similarity.
- Rule-based information extraction with regex: monetary magnitude (normalised
  to crore), years, and known organisations (NHAI, AAI, Indian Railways, ...).
- A weighted project-type classifier + project-status classifier that together
  produce an impact score (0-100) and an estimated lead time (years before the
  price effect typically lands).

What is NOT here (by design)
----------------------------
- A fine-tuned transformer (BERT/LLaMA). That needs a labelled corpus + GPU and
  multi-GB weights, which are out of scope for the MVP. The interfaces below are
  the same ones a transformer-backed implementation would expose, so it can be
  swapped in later without touching the API.
"""
from __future__ import annotations

import re
import threading
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..data.cities_data import get_all_cities
from .sample_signals import CORPUS

# ── taxonomies ──────────────────────────────────────────────────────────────
PROJECT_TYPES: dict[str, dict] = {
    "airport":             {"weight": 90, "kw": ["airport", "terminal", "runway", "airstrip", "greenfield airport"]},
    "metro_rail":          {"weight": 85, "kw": ["metro", "rapid transit", "mrts"]},
    "industrial_corridor": {"weight": 88, "kw": ["industrial corridor", "industrial park", "industrial zone", "sez", "textile park", "nicdc", "dmic", "gati shakti", "node", "cluster", "bourse", "refinery", "logistics"]},
    "expressway":          {"weight": 78, "kw": ["expressway", "ring road", "bypass", "six-lane", "four-lane", "national highway", "nh-", "nhai", "nhidcl", "elevated road", "access road", "interchange", "bridge", "samruddhi", "link expressway"]},
    "railway":             {"weight": 66, "kw": ["railway", "rail line", "broad-gauge", "electrification", "ircon", "railway station", "junction", "rail"]},
    "smart_city":          {"weight": 70, "kw": ["smart city", "amrut", "command centre", "command center", "urban transport", "ropeway", "it park"]},
    "realty":              {"weight": 48, "kw": ["rera", "registrations", "plotting", "layout", "township", "residential", "housing"]},
}

# (keywords, lead_time_years, certainty, label) — checked most-mature first
STATUS_RULES: list[tuple[list[str], int, float, str]] = [
    (["inaugurated", "operational", "completed", "commissioned", "opened", "fully operational"], 1, 0.95, "operational"),
    (["under construction", "construction begins", "construction beginning", "trial run", "nearing completion", "foundation"], 3, 0.85, "under_construction"),
    (["approved", "sanctioned", "awarded", "cleared", "notified", "allocated", "released", "acquisition is completed", "acquisition completed"], 4, 0.75, "approved"),
    (["tender", "bid", "dpr", "detailed project report", "submitted"], 5, 0.60, "tendering"),
    (["proposed", "feasibility", "survey", "planned", "pre-feasibility", "under preparation", "commissioned"], 6, 0.45, "proposed"),
]

_MONEY_RE = re.compile(r"(?:₹|rs\.?|inr)\s?([\d,]+(?:\.\d+)?)\s?(crore|cr|lakh|lakhs|billion|bn)?", re.I)
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_ORG_RE = re.compile(r"\b(NHAI|NHIDCL|AAI|IRCON|NICDC|DMIC|RERA|PM Gati Shakti|Indian Railways|AMRUT|SEZ|MADC|Smart City)\b", re.I)

_KNOWN_PLACES: list[tuple[str, str]] = []  # (lowercased name, kind) filled at import


def _money_to_crore(num_str: str, unit: str | None) -> float:
    try:
        val = float(num_str.replace(",", ""))
    except ValueError:
        return 0.0
    unit = (unit or "crore").lower()
    if unit in ("lakh", "lakhs"):
        return val / 100.0
    if unit in ("billion", "bn"):
        return val * 100.0
    return val  # crore / cr


def _extract_entities(text: str) -> dict[str, Any]:
    amounts = [round(_money_to_crore(m.group(1), m.group(2)), 2) for m in _MONEY_RE.finditer(text)]
    amounts = [a for a in amounts if a > 0]
    years = sorted({int(y) for y in _YEAR_RE.findall(text)})
    orgs = sorted({m.group(1).upper() if m.group(1).isupper() else m.group(1).title() for m in _ORG_RE.finditer(text)})
    tl = text.lower()
    places = sorted({name.title() for name, _ in _KNOWN_PLACES if name in tl})
    return {
        "amounts_inr_crore": amounts,
        "max_amount_inr_crore": max(amounts) if amounts else None,
        "years": years,
        "organizations": orgs,
        "locations": places,
    }


def _classify_project(text: str) -> tuple[str, int, list[str]]:
    tl = text.lower()
    best_type, best_score, best_kw = "other", 0.0, []
    for ptype, cfg in PROJECT_TYPES.items():
        hits = [kw for kw in cfg["kw"] if kw in tl]
        if not hits:
            continue
        score = cfg["weight"] + (len(hits) - 1) * 3
        if score > best_score:
            best_type, best_score, best_kw = ptype, score, hits
    base_weight = PROJECT_TYPES.get(best_type, {"weight": 40})["weight"]
    return best_type, base_weight, best_kw


def _classify_status(text: str) -> tuple[str, int, float]:
    tl = text.lower()
    for kws, lead, certainty, label in STATUS_RULES:
        if any(k in tl for k in kws):
            return label, lead, certainty
    return "proposed", 6, 0.45


def analyze_text(text: str) -> dict[str, Any]:
    """Turn one free-text announcement into a structured, scored signal."""
    ptype, base_weight, matched_kw = _classify_project(text)
    status, lead_years, certainty = _classify_status(text)
    entities = _extract_entities(text)

    # impact = project weight tempered by certainty, plus a magnitude bonus
    mag = entities["max_amount_inr_crore"] or 0
    mag_bonus = 12 if mag >= 5000 else 8 if mag >= 1000 else 4 if mag >= 500 else 0
    impact = base_weight * certainty + mag_bonus
    impact = round(max(0.0, min(impact, 100.0)), 1)

    return {
        "project_type": ptype,
        "status": status,
        "impact_score": impact,
        "lead_time_years": lead_years,
        "certainty": certainty,
        "matched_keywords": matched_kw,
        "entities": entities,
    }


# ── TF-IDF index over the corpus (fit once) ─────────────────────────────────
class _Index:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.docs = CORPUS

    def ensure_built(self) -> None:
        if self.vectorizer is not None:
            return
        with self._lock:
            if self.vectorizer is not None:
                return
            self.vectorizer = TfidfVectorizer(
                stop_words="english", ngram_range=(1, 2), min_df=1, max_df=0.9
            )
            self.matrix = self.vectorizer.fit_transform([d["text"] for d in self.docs])

    def similarities(self, query: str) -> np.ndarray:
        self.ensure_built()
        qv = self.vectorizer.transform([query])
        return cosine_similarity(qv, self.matrix)[0]

    def top_terms(self, n: int = 15) -> list[dict]:
        self.ensure_built()
        vocab = np.array(self.vectorizer.get_feature_names_out())
        weights = np.asarray(self.matrix.sum(axis=0)).ravel()
        order = np.argsort(weights)[::-1][:n]
        return [{"term": vocab[i], "weight": round(float(weights[i]), 3)} for i in order]


_INDEX = _Index()


def _city_query(city: dict) -> str:
    parts = [
        city["name"], city["state"],
        city["infrastructure"].get("industry_type", ""),
        city.get("nearest_metro", ""),
        " ".join(city.get("government_schemes", [])),
        " ".join(city.get("growth_triggers", [])),
    ]
    return " ".join(p for p in parts if p)


def _synth_signals(city: dict) -> list[dict]:
    """Derive baseline signals from a city's own infrastructure profile so every
    city surfaces at least a few indicators even without a corpus match."""
    out: list[dict] = []
    infra = city["infrastructure"]
    schemes = city.get("government_schemes", [])
    name = city["name"]

    if infra.get("has_airport"):
        out.append((f"{name} has operational airport connectivity supporting business travel and cargo.", "AAI"))
    if "Smart City" in schemes:
        out.append((f"{name} is funded under the Smart City Mission with approved urban infrastructure works.", "Smart City Mission"))
    if "AMRUT" in schemes:
        out.append((f"AMRUT scheme funds were allocated to {name} for water, sewerage and road upgrades.", "AMRUT"))
    if infra.get("num_national_highways", 0) >= 2:
        out.append((f"{name} sits at a national highway junction with {infra['num_national_highways']} NH links improving connectivity.", "NHAI"))
    if infra.get("has_railway"):
        out.append((f"{name} has railway connectivity; station upgrades are part of the modernisation programme.", "Indian Railways"))
    if city["tier"] == 3 and city["growth_phase"] == "emerging":
        out.append((f"{name} is an emerging Tier-3 market with early-stage plotting and rising RERA registrations.", "RERA"))

    signals = []
    for text, source in out:
        sig = analyze_text(text)
        sig.update({
            "id": f"synth_{city['id']}_{sig['project_type']}",
            "headline": text,
            "source": source,
            "year": 2024,
            "origin": "city_profile",
            "relevance": 1.0,
        })
        signals.append(sig)
    return signals


def signals_for_city(city: dict, top: int = 6) -> dict[str, Any]:
    """Return ranked infrastructure signals relevant to a city."""
    sims = _INDEX.similarities(_city_query(city))

    matched: list[dict] = []
    for i, doc in enumerate(CORPUS):
        cos = float(sims[i])
        location_match = (doc.get("city_id") == city["id"])
        state_match = (doc.get("state") == city["state"])
        relevance = cos + (0.6 if location_match else 0.0) + (0.15 if state_match else 0.0)
        if not (location_match or state_match or cos > 0.07):
            continue
        sig = analyze_text(doc["text"])
        sig.update({
            "id": doc["id"],
            "headline": doc["text"],
            "source": doc["source"],
            "year": doc["year"],
            "origin": "corpus",
            "relevance": round(relevance, 3),
        })
        matched.append(sig)

    combined = matched + _synth_signals(city)
    # de-dup by headline, keep highest impact
    seen: dict[str, dict] = {}
    for s in combined:
        key = s["headline"][:60]
        if key not in seen or s["impact_score"] > seen[key]["impact_score"]:
            seen[key] = s
    ranked = sorted(seen.values(), key=lambda s: (s["impact_score"], s["relevance"]), reverse=True)[:top]

    if ranked:
        composite = round(sum(s["impact_score"] for s in ranked) / len(ranked), 1)
        soonest = min(s["lead_time_years"] for s in ranked)
    else:
        composite, soonest = 0.0, None

    return {
        "city_id": city["id"],
        "city_name": city["name"],
        "signal_count": len(ranked),
        "composite_signal_score": composite,
        "soonest_impact_years": soonest,
        "signals": ranked,
    }


def corpus_stats() -> dict[str, Any]:
    """Global NLP stats: corpus size and top TF-IDF terms."""
    return {
        "documents": len(CORPUS),
        "method": "tfidf(1,2-gram) + rule-based extraction",
        "top_terms": _INDEX.top_terms(15),
    }


def _init_places() -> None:
    for c in get_all_cities():
        _KNOWN_PLACES.append((c["name"].lower(), "city"))
    for s in {c["state"] for c in get_all_cities()}:
        _KNOWN_PLACES.append((s.lower(), "state"))


_init_places()
