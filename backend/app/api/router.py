from fastapi import APIRouter
from backend.app.api.v1 import (
    health,
    models,
    generate,
    claims,
    verify,
    correct,
    documents,
    evaluations,
    datasets
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(models.router, tags=["Models"])
api_router.include_router(generate.router, tags=["Generate"])
api_router.include_router(claims.router, tags=["Claims"])
api_router.include_router(verify.router, tags=["Verification"])
api_router.include_router(correct.router, tags=["Correction"])
api_router.include_router(documents.router, tags=["Documents"])
api_router.include_router(evaluations.router, tags=["Evaluations"])
api_router.include_router(datasets.router, tags=["Datasets"])

