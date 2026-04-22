from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI
from pydantic import BaseModel, Field

APP_VERSION = "1.1.0"

app = FastAPI(
    title="Lead Prioritization API",
    description="Scores inbound leads to support sales prioritization.",
    version=APP_VERSION,
)


class LeadFeatures(BaseModel):
    annual_revenue_k: float = Field(ge=0, description="Annual revenue in kUSD.")
    employees: int = Field(ge=1, description="Company size.")
    segment: str = Field(description='Company segment: "enterprise", "smb", or "startup".')
    has_urgent_need: bool = Field(description="Time-sensitive business need.")
    contact_email_verified: bool = Field(description="Inbound data quality signal.")


class PrioritizationRequest(BaseModel):
    lead_id: str = Field(min_length=1)
    features: LeadFeatures
    force_strategy: Optional[str] = Field(
        default=None,
        description='Optional override: "model" | "rules" | "heuristic".',
    )


class PrioritizationResponse(BaseModel):
    lead_id: str
    score: float
    priority: str
    strategy_used: str
    explanation: List[str]
    limitations: List[str]


def _normalize_segment(segment: str) -> str:
    return segment.strip().lower()


def _model_score(features: LeadFeatures) -> Optional[Tuple[float, str, List[str]]]:
    if not features.contact_email_verified and features.employees < 5:
        return None

    segment_weight: Dict[str, float] = {
        "enterprise": 0.35,
        "smb": 0.2,
        "startup": 0.1,
    }
    segment = _normalize_segment(features.segment)
    if segment not in segment_weight:
        return None

    urgency_bonus = 0.2 if features.has_urgent_need else 0.0
    revenue_factor = min(features.annual_revenue_k / 10_000, 0.3)
    size_factor = min(features.employees / 5_000, 0.15)
    quality_penalty = -0.1 if not features.contact_email_verified else 0.0

    score = max(
        0.0,
        min(
            1.0,
            segment_weight[segment]
            + urgency_bonus
            + revenue_factor
            + size_factor
            + quality_penalty,
        ),
    )
    return (
        score,
        "model",
        ["Weighted score across segment, urgency, size, and data quality."],
    )


def _rules_score(features: LeadFeatures) -> Optional[Tuple[float, str, List[str]]]:
    segment = _normalize_segment(features.segment)

    if segment == "enterprise" and features.has_urgent_need:
        score = 0.92
        reason = "Enterprise + urgent need is treated as top priority."
    elif segment == "smb" and features.annual_revenue_k >= 500:
        score = 0.74
        reason = "SMB above revenue threshold matches expansion policy."
    elif segment == "startup" and features.employees < 10:
        score = 0.35
        reason = "Early startup is queued for later qualification."
    else:
        return None

    if not features.contact_email_verified:
        score = max(0.0, score - 0.1)
        reason += " Score adjusted for unverified email."

    return (score, "rules", [reason])


def _heuristic_fallback(features: LeadFeatures) -> Tuple[float, str, List[str]]:
    segment = _normalize_segment(features.segment)
    base = 0.5
    if features.has_urgent_need:
        base += 0.15
    if features.contact_email_verified:
        base += 0.05
    if segment == "enterprise":
        base += 0.1
    return (
        min(1.0, base),
        "heuristic",
        ["Fallback keeps the API stable when strong signals are missing."],
    )


def _to_priority(score: float) -> str:
    if score >= 0.8:
        return "P1"
    if score >= 0.6:
        return "P2"
    return "P3"


@app.get("/")
def service_info() -> Dict[str, str]:
    return {
        "service": "Lead Prioritization API",
        "business_value": "Improves sales response time by ranking leads consistently.",
        "version": APP_VERSION,
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "utc_time": datetime.now(timezone.utc).isoformat()}


@app.post("/prioritize", response_model=PrioritizationResponse)
def prioritize_lead(payload: PrioritizationRequest) -> PrioritizationResponse:
    features = payload.features
    forced = payload.force_strategy.lower().strip() if payload.force_strategy else None

    if forced == "model":
        result = _model_score(features) or _heuristic_fallback(features)
    elif forced == "rules":
        result = _rules_score(features) or _heuristic_fallback(features)
    elif forced == "heuristic":
        result = _heuristic_fallback(features)
    else:
        result = _model_score(features) or _rules_score(features) or _heuristic_fallback(
            features
        )

    score, strategy_name, explanation = result

    return PrioritizationResponse(
        lead_id=payload.lead_id,
        score=round(score, 3),
        priority=_to_priority(score),
        strategy_used=strategy_name,
        explanation=explanation,
        limitations=[
            "Rule-based scoring, not a trained production model.",
            "No drift monitoring or retraining loop yet.",
            "Limited feature set may miss domain-specific signals.",
            "Fallback improves uptime but can reduce ranking accuracy.",
        ],
    )