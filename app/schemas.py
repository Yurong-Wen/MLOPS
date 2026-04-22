from typing import Literal

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    symbol: str = Field(..., description="Ticker symbol, e.g. AAPL")
    days: int = Field(30, ge=1, le=3650, description="Forecast horizon in days")


class PredictResponse(BaseModel):
    predicted_price: float
    prediction_source: Literal["model", "fallback"]

