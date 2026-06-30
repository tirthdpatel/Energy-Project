"""India Energy Atlas — FastAPI backend entry point (v0.5.0)."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.energy import router as energy_router
from routers.power_plants import router as power_plants_router
from routers.analytics import router as analytics_router
from routers.insights import router as insights_router
from routers.market import router as market_router
from routers.live_generation import router as live_generation_router

# Allow the frontend origin to be configured via environment variable,
# falling back to localhost for local development.
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

app = FastAPI(
    title="India Energy Atlas API",
    version="0.5.0",
    description="REST API serving Indian state-level energy data, analytics, and GeoJSON boundaries.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(energy_router)
app.include_router(power_plants_router)
app.include_router(analytics_router)
app.include_router(insights_router)
app.include_router(market_router, prefix="/api/market", tags=["market"])
app.include_router(live_generation_router, prefix="/api/generation", tags=["live"])


@app.get("/")
def root():
    return {"message": "India Energy Atlas API v0.5.0 is running."}
