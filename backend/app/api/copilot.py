from fastapi import APIRouter, Body, HTTPException, Query

from ..services.copilot import query as copilot_query

router = APIRouter(prefix="/copilot", tags=["copilot"])

_EXAMPLES = [
    "Best city under ₹20 lakh near a metro",
    "Low-risk Tier-2 cities in Gujarat",
    "Highest ROI emerging towns",
    "Alternatives to Bangalore",
    "Cheap cities with high growth potential",
]


@router.get("/examples")
def examples():
    return {"examples": _EXAMPLES}


@router.post("/query")
def run_query(payload: dict = Body(..., example={"query": "best city under 20 lakh near a metro", "top": 6})):
    q = (payload or {}).get("query", "").strip()
    if not q:
        raise HTTPException(400, detail="Body must include a non-empty 'query' field")
    top = int((payload or {}).get("top", 6))
    return copilot_query(q, max(1, min(top, 20)))


@router.get("/query")
def run_query_get(q: str = Query(...), top: int = Query(6, ge=1, le=20)):
    return copilot_query(q.strip(), top)
