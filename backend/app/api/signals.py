from fastapi import APIRouter, Body, HTTPException, Query

from ..data.cities_data import get_city
from ..nlp.signal_parser import analyze_text, corpus_stats, signals_for_city

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("/")
def signals_overview():
    """Corpus-level NLP statistics (document count + top TF-IDF terms)."""
    return corpus_stats()


@router.post("/analyze")
def analyze(payload: dict = Body(..., example={"text": "NHAI approved the Rs 3200 crore Patna ring road; tenders awarded."})):
    """Parse an arbitrary infrastructure announcement into a structured signal."""
    text = (payload or {}).get("text", "").strip()
    if not text:
        raise HTTPException(400, detail="Body must include a non-empty 'text' field")
    return {"input": text, "signal": analyze_text(text)}


@router.get("/{city_id}")
def city_signals(city_id: str, top: int = Query(6, ge=1, le=12)):
    """Ranked infrastructure leading-indicator signals for a city."""
    city = get_city(city_id)
    if not city:
        raise HTTPException(404, detail=f"City '{city_id}' not found")
    return signals_for_city(city, top)
