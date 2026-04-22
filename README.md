# Finance Forecast API

FastAPI service that predicts a future price from `symbol` and `days`.

- If `app/model.pkl` is available and loadable, predictions come from that model.
- If the model is missing or fails to load, the service falls back to a deterministic heuristic so the API still responds.

## Business Case

This project is intentionally lightweight, but maps to a real product need:

- **Use case:** provide a quick forecast estimate for dashboards, simulations, or early-stage product experiments.
- **Value:** downstream users get one stable API contract (`/predict`) regardless of model availability.
- **Operational benefit:** fallback behavior avoids hard downtime during model packaging/deployment issues, which is useful in small teams or demo environments.

This is not intended to replace production-grade quantitative forecasting; it is a baseline service architecture with graceful degradation.

## Why This Design

The core design has two prediction paths:

1. **Primary path: trained model (`model.pkl`)**
   - Preferred when available.
   - Represents the "best effort" predictive logic.
2. **Fallback path: heuristic**
   - Keeps API behavior available when model artifacts are unavailable or corrupted.
   - Produces deterministic outputs for predictable behavior and easier debugging.

Why this trade-off:

- **Reliability over strict accuracy guarantees:** clients always get a response.
- **Simple interface for consumers:** no endpoint switching; same request/response schema.
- **Low implementation complexity:** easier to understand and maintain for a minimal submission.

## Project Layout

```text
.
├── app/
│   ├── main.py      # API routes and readiness behavior
│   ├── schemas.py   # Request/response validation schemas
│   ├── model.py     # Thin model facade
│   └── scoring.py   # Model loading + fallback heuristic
├── requirements.txt
└── Dockerfile
```

## API Endpoints

- `POST /predict`
  - Input: `symbol` (string), `days` (int, 1..3650)
  - Output:
    - `predicted_price` (float)
    - `prediction_source` (`model` or `fallback`)
- `GET /health`
  - Returns `200` when API process is running.
- `GET /ready`
  - Returns `200` when the model is loaded.
  - Returns `503` when the service is in fallback-only mode.

## Local Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Example request:

```bash
curl -X POST http://127.0.0.1:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","days":30}'
```

## Docker

```bash
docker build -t finance-forecast-api .
docker run --rm -p 8080:8080 finance-forecast-api
```

## Limitations and Risks

- **Fallback is not a financial model:** heuristic outputs are synthetic and can be far from market reality.
- **No confidence/uncertainty reporting:** API returns a single point estimate only.
- **Minimal validation of symbol quality:** format is accepted, but ticker existence/market context is not checked.
- **No offline/online evaluation loop:** there is no current mechanism to track model drift or forecast quality over time.

## Maintainability and Operations Guidance

For a stronger production path, prioritize:

1. **Observability**
   - Current state: fallback usage is logged as a warning in API logs.
   - Next step: add structured logs for request IDs and latency.
   - Expose basic metrics (request count, error rate, fallback usage rate).
2. **Model lifecycle**
   - Version model artifacts and publish metadata (training date, feature schema, expected input types).
   - Add a startup check to fail fast (or warn clearly) when expected artifacts are missing.
3. **Testing**
   - Unit tests for schema validation and scoring behavior.
   - Contract tests for `/predict` and `/ready`.
   - Regression tests to verify deterministic fallback output.
4. **Safety and product UX**
   - Include response metadata indicating prediction source (`model` or `fallback`).
   - Document that outputs are for informational/demo usage, not investment advice.

## Suggested Next Iteration

- Add a simple test suite (`pytest`) and CI checks.
- Add model artifact metadata in readiness output (model version, build date).
- Add basic metrics endpoint (or Prometheus integration) for operational visibility.