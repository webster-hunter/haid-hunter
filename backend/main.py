import logging
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from backend.auth import require_auth
from backend.rate_limit import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
from backend.config import DOCUMENTS_DIR, DATA_DIR
from backend.routers.documents import router as documents_router
from backend.routers.tags import router as tags_router
from backend.routers.profile import router as profile_router, skills_router
from backend.routers.applications import router as applications_router
from backend.routers.settings import router as settings_router
from backend.routers.tasks import router as tasks_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.extraction import router as extraction_router
from backend.services.database import init_db
from backend.services.encryption import EncryptionService

app = FastAPI(title="hAId-hunter API", dependencies=[Depends(require_auth)])
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


app.include_router(documents_router)
app.include_router(tags_router)
app.include_router(profile_router)
app.include_router(applications_router)
app.include_router(settings_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
app.include_router(extraction_router)
app.include_router(skills_router)


@app.on_event("startup")
async def startup():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    init_db()
    # Ensure encryption key is generated immediately on startup (not deferred to first request)
    EncryptionService()


@app.get("/api/health")
async def health():
    return {"status": "ok"}
