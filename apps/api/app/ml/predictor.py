from datetime import datetime, timezone
from typing import Any

from app.ml.model import RiskModel
from app.schemas.risk import RiskAssessment, RiskFactor


class RiskPredictor:
    """Thin wrapper: model loading and prediction only (AGENTS.md section 9).

    Never triggers or authorizes actions. Output includes score, band, top
    factors, model version, ``calibrated``, and a source marker so placeholder
    vs real model output is distinguishable.
    """

    def __init__(self, model: RiskModel | None = None) -> None:
        self.model = model or RiskModel()

    def assess(
        self,
        *,
        transaction_id: str,
        features: dict[str, Any],
        as_of: datetime | None = None,
    ) -> RiskAssessment:
        if "transaction_id" not in features:
            features = {"transaction_id": transaction_id, **features}
        raw = self.model.predict(features)
        source = "placeholder" if raw.get("fallback_used") else "ml_model"
        return RiskAssessment(
            transaction_id=transaction_id,
            score=raw["score"],
            band=raw["band"],
            top_factors=[
                RiskFactor(**f) if isinstance(f, dict) else f
                for f in raw.get("top_factors", [])
            ],
            model_version=raw["model_version"],
            calibrated=bool(raw.get("calibrated", False)),
            source=source,
            fallback_used=bool(raw.get("fallback_used", False)),
            generated_at=as_of or datetime.now(timezone.utc),
        )