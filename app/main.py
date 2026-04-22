from fastapi import FastAPI, HTTPException, status, Response
from schemas import PredictRequest, PredictResponse
from model import FinanceModel

app = FastAPI(title="Finance Forecast API", version="0.1.0")
model = FinanceModel()

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    try:
        price = model.predict(symbol=req.symbol.upper(), days=req.days)
    except Exception:
        raise HTTPException(status_code=500, detail="prediction failed")
    return PredictResponse(predicted_price=float(price))

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