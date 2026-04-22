import logging

from fastapi import FastAPI, HTTPException, Response, status

from app.model import FinanceModel
from app.schemas import PredictRequest, PredictResponse

app = FastAPI(title="Finance Forecast API", version="0.1.0")
model = FinanceModel()
logger = logging.getLogger(__name__)

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        source = model.prediction_source()
        price = model.predict(symbol=req.symbol.upper(), days=req.days)
    except Exception:
        raise HTTPException(status_code=500, detail="prediction failed")
    if source == "fallback":
        logger.warning("Using fallback heuristic for prediction")
    return PredictResponse(predicted_price=float(price), prediction_source=source)


@app.get("/health")
def health():
    return {"status": "up"}

@app.get("/ready")
def readiness():
    model_loaded = model.is_ready()
    if not model_loaded:
        return Response(
            content='{"status":"unready","model_loaded":false}',
            media_type="application/json",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return {"status": "ready", "model_loaded": True}