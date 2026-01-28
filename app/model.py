from scoring import Scorer


class FinanceModel:
    def __init__(self):
        self._scorer = Scorer()

    def is_ready(self) -> bool:
        return self._scorer.is_ready()

    def predict(self, symbol: str, days: int) -> float:
        return self._scorer.predict(symbol=symbol, days=days)

