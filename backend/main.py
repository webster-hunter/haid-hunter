from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import DOCUMENTS_DIR, DATA_DIR

app = FastAPI(title="hAId-hunter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
