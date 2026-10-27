from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.schemas.evaluation import (
    FEVERStatusResponse,
    FEVERPrepareRequest,
    FEVERIndexRequest,
    HaluEvalStatusResponse
)
from backend.app.services.evaluation_service import evaluation_service
from backend.app.datasets.fever_loader import fever_loader
from backend.app.datasets.fever_evidence_indexer import fever_indexer
from backend.app.nlp.retriever import fever_retriever

router = APIRouter()


@router.get("/datasets/halueval/status", response_model=HaluEvalStatusResponse)
def get_halueval_status():
    """Returns local HaluEval dataset availability, file paths, and record counts across tasks."""
    try:
        tasks_status = evaluation_service.get_halueval_status()
        is_available = any(t.get("available", False) for t in tasks_status.values())
        total_records = sum(t.get("total_records", 0) for t in tasks_status.values() if t.get("available"))
        return {
            "is_available": is_available,
            "total_records": total_records,
            "tasks": tasks_status
        }
    except Exception as e:
        logger.error(f"Failed to check HaluEval status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets/fever/status", response_model=FEVERStatusResponse)
def get_fever_status():
    """Returns local FEVER dataset download, preparation, and FAISS indexing status."""
    try:
        status_dict = evaluation_service.get_fever_status()
        return FEVERStatusResponse(**status_dict)
    except Exception as e:
        logger.error(f"Failed to check FEVER status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/datasets/fever/prepare")
def prepare_fever_dataset(req: FEVERPrepareRequest):
    """Downloads (if needed) and prepares a reproducible FEVER dataset split sample."""
    try:
        out_path, summary = fever_loader.prepare_dataset(
            split=req.split or "paper_dev",
            limit=req.limit or 1000,
            seed=req.seed or 42,
            force_download=req.force_download or False
        )
        return {
            "status": "success",
            "message": f"Successfully prepared FEVER {req.split} sample with {summary.get('sample_size')} items.",
            "file_path": str(out_path),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"FEVER preparation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Preparation failed: {str(e)}")


@router.post("/datasets/fever/index")
def index_fever_evidence(req: FEVERIndexRequest):
    """Builds the dedicated FEVER Knowledge Base FAISS index from prepared verification evidence."""
    input_path = settings.DATASETS_PATH / "fever" / "prepared" / f"fever_{req.split}_{req.limit}.jsonl"
    if not input_path.exists():
        prep_files = list((settings.DATASETS_PATH / "fever" / "prepared").glob("*.jsonl"))
        if prep_files:
            input_path = prep_files[0]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Prepared FEVER file not found at {input_path}. Please run dataset preparation first."
            )

    try:
        summary = fever_indexer.build_index_from_prepared_dataset(
            prepared_dataset_path=input_path,
            max_articles=req.max_articles,
            rebuild=req.rebuild if req.rebuild is not None else True
        )
        return {
            "status": "success",
            "message": "FEVER Knowledge Base successfully indexed into FAISS.",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"FEVER indexing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.delete("/datasets/fever/index")
def clear_fever_index():
    """Safely clears the FEVER FAISS index."""
    try:
        fever_retriever.clear()
        summary_path = settings.INDEXES_PATH / "fever_knowledge_base_summary.json"
        if summary_path.exists():
            summary_path.unlink()
        return {"status": "success", "message": "FEVER Knowledge Base FAISS index cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")
