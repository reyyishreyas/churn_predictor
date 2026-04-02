# Churn Predictor

FastAPI backend and Streamlit UI for telco-style churn scoring: single predictions, batch CSV, optional Gmail SMTP for retention mail, and a small what-if simulator.

## Stack

- Backend: Python 3.11+, FastAPI, scikit-learn, XGBoost/LightGBM (training), joblib
- UI: Streamlit
- Data: `data/churn.csv` (or your own CSV following the same schema)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Train models and write artifacts under `backend/artifacts/`:

```bash
python backend/train_pipeline.py
```

Copy `backend/.env.example` to `backend/.env` and set Gmail variables if you want real email from batch jobs.

Run API (from repo root):

```bash
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run UI (separate terminal):

```bash
export CHURN_API_URL=http://localhost:8000
streamlit run frontend/app.py
```

## API

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/predict` | Single customer churn score and actions |
| POST | `/simulate` | What-if with field overrides |
| POST | `/batch-predict` | CSV upload, predictions, optional emails |
| GET | `/insights` | Dataset-level metrics |
| GET | `/model-metrics` | Model comparison metrics |
| GET | `/health` | Health check |

Open `/docs` on the API host for interactive schemas.

## Environment

Common variables (see `backend/.env.example`):

- `CHURN_TRIGGER_THRESHOLD` — probability above which interventions trigger (default `0.6`)
- `GMAIL_ADDRESS` / `GMAIL_APP_PASSWORD` — Gmail app password for SMTP
- `EMAIL_BATCH_MIN_RISK` — `threshold`, `medium`, or `high` for batch email targeting

Do not commit `backend/.env` or generated logs.

## Layout

```
backend/app/     FastAPI app (routes, services, config)
backend/artifacts/   Trained models (generated, not committed)
data/            Training CSV
frontend/        Streamlit app
notebooks/       Reference notebook
```

## License

Add a `LICENSE` file if you publish this project.
