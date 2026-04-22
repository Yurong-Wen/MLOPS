# Lead Prioritization API

## Why This Exists

Sales teams lose time when every inbound lead is treated equally. This API ranks
leads so first contact is faster and more consistent.

## Scoring Approach

The service combines three paths:
- `model`: weighted score from segment, urgency, revenue, size, and data quality.
- `rules`: fixed business rules for known commercial cases.
- `heuristic`: fallback when confidence is low or rules are inconclusive.

This keeps the output explainable while avoiding service gaps.

## Endpoints

- `GET /` - service metadata and business value
- `GET /health` - health check
- `POST /prioritize` - score, priority (`P1`/`P2`/`P3`), strategy, explanation, limitations

## Run

```bash
uvicorn main:app --reload
```

```bash
curl -X POST "http://127.0.0.1:8000/prioritize" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead-123",
    "features": {
      "annual_revenue_k": 1800,
      "employees": 220,
      "segment": "smb",
      "has_urgent_need": true,
      "contact_email_verified": true
    }
  }'
```

## Limits and Next Steps

Current limits:
- scoring is handcrafted, not trained from conversion history,
- no drift monitoring or retraining loop,
- small feature set.

Recommended next steps:
- add unit tests for threshold and fallback behavior,
- log strategy usage and response latency,
- evaluate on historical data and tune weights/rules.