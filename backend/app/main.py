from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.cities import router as cities_router
from .api.copilot import router as copilot_router
from .api.cv import router as cv_router
from .api.geo import router as geo_router
from .api.live import router as live_router
from .api.ml import router as ml_router
from .api.predictions import router as predictions_router
from .api.score import router as score_router
from .api.signals import router as signals_router
from .api.system import router as system_router
from . import ratelimit
from .metrics import RequestMetricsMiddleware
from .data.cities_data import get_all_cities
from .geo.db import init_and_seed, spatial_backend_status
from .db import init_db
from .auth.routes import account_router, auth_router, keys_router
from .api.v1 import router as v1_router
from .billing.webhooks import router as billing_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Observability first: structured logging (LOG_JSON) + error tracking (SENTRY_DSN).
    try:
        from . import obs

        obs.configure_logging()
        obs.init_error_tracking()
    except Exception:
        pass
    # Create auth/platform tables (SQLite by default; Postgres via DATABASE_URL).
    try:
        init_db()
    except Exception:
        pass
    # Startup migration health check — warn (never block) if the DB is behind head.
    try:
        import logging

        from .db import schema_status

        st = schema_status()
        if st.get("alembic") == "behind":
            logging.getLogger("landai").warning("DB schema is behind Alembic head: %s", st)
    except Exception:
        pass
    # Seed PostGIS if a database is attached (no-op for the default in-memory setup)
    try:
        init_and_seed(get_all_cities())
    except Exception:
        pass
    yield


app = FastAPI(
    title="LandAI API",
    description="AI-powered land-development prediction for Indian cities "
                "(XGBoost price model · NLP infrastructure signals · shapely/PostGIS geometry · CV urban-growth raster)",
    version="2.0.0",
    lifespan=lifespan,
)

# Inbound rate limiting (added before CORS so CORS stays the outermost layer
# and even 429 responses carry CORS headers). Toggle with RATELIMIT_ENABLED.
if ratelimit.ENABLED:
    app.add_middleware(ratelimit.RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Outermost: times the whole request (incl. rate-limit 429s), tags X-Request-ID.
app.add_middleware(RequestMetricsMiddleware)

for r in (cities_router, predictions_router, ml_router, signals_router,
          geo_router, cv_router, score_router, copilot_router, live_router,
          system_router, auth_router, keys_router, account_router,
          v1_router, billing_router):
    app.include_router(r, prefix="/api")


@app.get("/")
def root():
    return {
        "app": "LandAI",
        "version": "2.0.0",
        "description": "Urban growth prediction for Indian cities",
        "capabilities": {
            "cities": "/api/cities",
            "predictions": "/api/predictions",
            "ml_price_model_xgboost": "/api/ml",
            "nlp_infrastructure_signals": "/api/signals",
            "geo_postgis_shapely": "/api/geo",
            "cv_urban_growth_raster": "/api/cv",
            "investment_scoring": "/api/score",
            "ai_copilot": "/api/copilot",
            "live_data_ingestion_osm": "/api/live",
            "system_data_trust": "/api/system",
            "auth": "/api/auth",
            "api_keys": "/api/keys",
            "account": "/api/account",
            "developer_api_metered": "/api/v1",
            "billing_status": "/api/billing/status",
        },
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "spatial_backend": spatial_backend_status()["active_backend"]}
