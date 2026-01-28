# Finance Forecast API (quick, human-sized guide)

A tiny FastAPI app that fakes a price forecast for a ticker. If you drop a `model.pkl` (joblib) next to the code, it will use that; otherwise it falls back to a simple heuristic.

## What’s inside
```
app/               # project root (where Dockerfile lives)
  Dockerfile
  requirements.txt
  app/             # Python package
    main.py        # FastAPI app + routes
    schemas.py     # request/response shapes
    model.py       # FinanceModel wrapper
    scoring.py     # loads model or uses heuristic
```

## Run it locally (no fuss)
```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd app/app
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
Hit it at `http://localhost:8080/ready`.

## Docker (one way that just works)
```bash
cd app
docker build -t finance-forecast-api .
docker run --rm -p 9000:8080 finance-forecast-api
```
Then go to `http://localhost:9000/ready`.

## Quick calls to try
- Health: `GET /ready`
- Predict:
  ```bash
  curl -s -X POST http://localhost:9000/predict \
    -H "Content-Type: application/json" \
    -d '{"symbol":"AAPL","days":30}'
  ```

## Notes
- If you have a real model, drop `model.pkl` in the same folder as `scoring.py`.
- Feel free to add tests under `tests/` and run `pytest`.
