import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.database import get_db
from backend.app.database.models import EvaluationExperiment
from backend.app.schemas.evaluation import (
    EvaluationRunRequest,
    EvaluationExperimentSchema,
    MultiModelComparisonRequest,
    MultiModelComparisonResponse
)
from backend.app.services.evaluation_service import evaluation_service

router = APIRouter()


@router.post("/evaluations/compare", response_model=MultiModelComparisonResponse)
def compare_models_endpoint(req: MultiModelComparisonRequest):
    """
    Empirical multi-model comparison comparing NLI-only (DeBERTa), LLM-only (Ollama),
    and Hybrid Consensus Ensemble on identical benchmark instances.
    """
    try:
        res = evaluation_service.run_multi_model_comparison(
            benchmark_name=req.benchmark_name,
            task=req.task or "qa",
            sample_size=req.sample_size or 10,
            seed=req.seed or 42,
            llm_model=req.llm_model or "qwen3:8b"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-model comparison failed: {str(e)}")


@router.post("/evaluations/run", response_model=EvaluationExperimentSchema)
def run_evaluation(req: EvaluationRunRequest, db: Session = Depends(get_db)):
    try:
        experiment = evaluation_service.run_benchmark(
            db=db,
            benchmark_name=req.benchmark_name,
            sample_size=req.sample_size or 20,
            model_name=req.model_name or "cross-encoder/nli-deberta-v3-small",
            evidence_source=req.evidence_source or ("context" if req.benchmark_name.upper() == "HALUEVAL" else "fever"),
            split=req.split or "paper_dev",
            top_k=req.top_k or 3,
            task=req.task or "qa",
            seed=req.seed or 42,
            sampling_strategy=req.sampling_strategy or "balanced_sampled"
        )
        return experiment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/evaluations/{experiment_id}/predictions")
def get_evaluation_predictions(experiment_id: str, db: Session = Depends(get_db)):
    """Returns the individual example prediction items and explainable audit trail for an experiment."""
    exp = db.query(EvaluationExperiment).filter(EvaluationExperiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Evaluation experiment not found")
    metrics_data = json.loads(exp.metrics_json or "{}")
    return {
        "experiment_id": exp.id,
        "name": exp.name,
        "benchmark_name": exp.benchmark_name,
        "total_samples": exp.total_samples,
        "predictions": metrics_data.get("predictions", [])
    }


@router.get("/evaluations", response_model=List[EvaluationExperimentSchema])
def list_evaluations(db: Session = Depends(get_db)):
    experiments = db.query(EvaluationExperiment).order_by(desc(EvaluationExperiment.created_at)).all()
    results = []
    for exp in experiments:
        results.append(EvaluationExperimentSchema(
            id=exp.id,
            name=exp.name,
            benchmark_name=exp.benchmark_name,
            model_name=exp.model_name,
            total_samples=exp.total_samples,
            accuracy=exp.accuracy,
            precision=exp.precision,
            recall=exp.recall,
            f1_score=exp.f1_score,
            retrieval_recall_at_k=exp.retrieval_recall_at_k,
            confusion_matrix=json.loads(exp.confusion_matrix_json),
            metrics=json.loads(exp.metrics_json),
            latency_per_sample_ms=exp.latency_per_sample_ms,
            created_at=exp.created_at
        ))
    return results


@router.get("/evaluations/{experiment_id}", response_model=EvaluationExperimentSchema)
def get_evaluation(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.query(EvaluationExperiment).filter(EvaluationExperiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Evaluation experiment not found")
    return EvaluationExperimentSchema(
        id=exp.id,
        name=exp.name,
        benchmark_name=exp.benchmark_name,
        model_name=exp.model_name,
        total_samples=exp.total_samples,
        accuracy=exp.accuracy,
        precision=exp.precision,
        recall=exp.recall,
        f1_score=exp.f1_score,
        retrieval_recall_at_k=exp.retrieval_recall_at_k,
        confusion_matrix=json.loads(exp.confusion_matrix_json),
        metrics=json.loads(exp.metrics_json),
        latency_per_sample_ms=exp.latency_per_sample_ms,
        created_at=exp.created_at
    )


@router.get("/evaluations/{experiment_id}/predictions")
def get_evaluation_predictions(experiment_id: str, db: Session = Depends(get_db)):
    """Returns sample-by-sample predictions for empirical audit and inspection."""
    exp = db.query(EvaluationExperiment).filter(EvaluationExperiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Evaluation experiment not found")
    metrics_data = json.loads(exp.metrics_json) if exp.metrics_json else {}
    return metrics_data.get("predictions", [])
