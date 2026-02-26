import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from api.v1.api import api_router
from core.config import settings
from core.db import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "**ManiocAgri** — plateforme de gestion agricole pour la ferme MOKPOKPO (Togo). "
        "Connecte producteurs, clients, livreurs, gestionnaires et agents terrain.\n\n"
        "**Rôles:** `admin`, `gestionnaire`, `producteur`, `agent`, `livreur`, `client`"
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─ must come BEFORE the API router and StaticFiles ─────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler ────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Veuillez réessayer."},
    )

# ── Startup ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    logger.info("🌱 ManiocAgri %s starting up...", settings.VERSION)
    init_db()
    logger.info("✅ Database initialized")


# ── API routes (registered BEFORE StaticFiles) ──────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_STR)

# ── Static files (frontend) ─ must be LAST ──────────────────────────────────
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
frontend_dir = os.path.join(project_root, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
    logger.info("📁 Static files mounted from: %s", frontend_dir)
else:
    logger.warning("Frontend directory not found at: %s", frontend_dir)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
