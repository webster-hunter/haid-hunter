from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import DOCUMENTS_DIR, DATA_DIR
from backend.routers.documents import router as documents_router
from backend.routers.tags import router as tags_router
from backend.routers.profile import router as profile_router
from backend.routers.interview import router as interview_router

app = FastAPI(title="hAId-hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(documents_router)
app.include_router(tags_router)
app.include_router(profile_router)
app.include_router(interview_router)


@app.on_event("startup")
async def startup():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
