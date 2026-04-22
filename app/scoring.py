from pathlib import Path

MODEL_PATH = Path(__file__).with_name("model.pkl")


class Scorer:
    def __init__(self):
        self._model = None
        if MODEL_PATH.exists():
            try:
                import joblib
                self._model = joblib.load(MODEL_PATH)
            except Exception:
                self._model = None

    def is_ready(self) -> bool:
        return self._model is not None

    def prediction_source(self) -> str:
        return "model" if self._model is not None else "fallback"

    def predict(self, symbol: str, days: int) -> float:
        if self._model is not None:
            X = [[symbol, days]]
            preds = self._model.predict(X)
            return float(preds[0])

        base = 50.0 + (sum(ord(c) for c in symbol) % 500)  # ~50..549
        drift_per_day = 0.0012  # ~0.12% per day
        return base * (1 + drift_per_day * days)