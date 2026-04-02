from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import (
    BatchPredictResponse,
    CustomerPayload,
    PredictionResponse,
    SimulationRequest,
    SimulationResponse,
)
from app.services.batch_service import run_batch_job
from app.services.insights_service import build_insights
from app.services.prediction_service import analyze_user
from app.services.simulation_service import run_simulation

router = APIRouter()


def _form_bool(raw: str | bool, *, default: bool) -> bool:
    if isinstance(raw, bool):
        return raw
    s = str(raw).strip().lower()
    if s == "":
        return default
    return s in ("1", "true", "yes", "on")


@router.post("/predict", response_model=PredictionResponse)
def predict(payload: CustomerPayload) -> dict:
    return analyze_user(payload.model_dump())


@router.post("/simulate", response_model=SimulationResponse)
def simulate(payload: SimulationRequest) -> dict:
    return run_simulation(payload.base_user.model_dump(), payload.updated_user.model_dump())


@router.get("/insights")
def insights() -> dict:
    return build_insights()


@router.get("/model-metrics")
def model_metrics() -> dict:
    return build_insights()["model_metrics"]


async def _batch_predict_handler(
    file: UploadFile = File(..., description="CSV with user_id, email, and all model feature columns."),
    send_emails: str = Form("true"),
    dry_run: str = Form("false"),
    include_enriched_csv: str = Form("true"),
) -> dict:
    name = (file.filename or "").lower()
    if not name.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload must be a .csv file.")
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file.")
    send_ok = _form_bool(send_emails, default=True)
    dry = _form_bool(dry_run, default=False)
    include_csv = _form_bool(include_enriched_csv, default=True)
    try:
        return run_batch_job(
            raw,
            send_emails=send_ok,
            dry_run=dry,
            include_enriched_csv=include_csv,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/batch-predict", response_model=BatchPredictResponse)
async def batch_predict(
    file: UploadFile = File(...),
    send_emails: str = Form("true"),
    dry_run: str = Form("false"),
    include_enriched_csv: str = Form("true"),
) -> dict:
    return await _batch_predict_handler(file, send_emails, dry_run, include_enriched_csv)


@router.post("/api/batch-predict", response_model=BatchPredictResponse)
async def batch_predict_api_alias(
    file: UploadFile = File(...),
    send_emails: str = Form("true"),
    dry_run: str = Form("false"),
    include_enriched_csv: str = Form("true"),
) -> dict:
    return await _batch_predict_handler(file, send_emails, dry_run, include_enriched_csv)
