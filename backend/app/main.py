import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.database import init_db, SessionLocal
from backend.app.nlp.retriever import sync_documents_index
from backend.app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema
    logger.info("Initializing TruthGuard database schema...")
    init_db()

    # Synchronize persistent FAISS and BM25 document indexes with SQLite
    db = SessionLocal()
    try:
        synced_chunks = sync_documents_index(db)
        logger.info(f"TruthGuard startup: verified and synchronized {synced_chunks} active document chunks in hybrid index.")
    except Exception as e:
        logger.error(f"Error synchronizing document indexes during startup: {e}", exc_info=True)
    finally:
        db.close()

    logger.info("TruthGuard backend startup complete.")
    yield
    logger.info("TruthGuard backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Explainable NLP Framework for Hallucination Detection, Evidence Verification, and Automatic Correction.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    
    response = await call_next(request)
    
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    return response


# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "framework": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "api_docs": "/docs",
        "api_v1": settings.API_V1_STR
    }
