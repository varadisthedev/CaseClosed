from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings


class RiskModel:
    """Loads a trained scikit-learn artifact if present, else deterministic stub.

    # PLACEHOLDER(ml-model): the stub returns a score derived from a hash of
    # the transaction ID; it is NOT calibrated (``calibrated=False``) and must
    # never be presented as a fraud probability (AGENTS.md section 9).
    """

    def __init__(self, model_path: str | None = None) -> None:
        settings = get_settings()
        self.model_path = Path(model_path or settings.ML_MODEL_PATH)
        self.model: Any | None = None
        self.loaded = False
        self.version = "unversioned"
        self._load_if_present()

    def _load_if_present(self) -> None:
        if not self.model_path.exists():
            self.model = None
            self.loaded = False
            self.version = f"stub-{self.model_path.stem or 'default'}"
            return
        artifact = joblib.load(self.model_path)
        self.model = artifact.get("model") if isinstance(artifact, dict) else artifact
        self.version = (
            artifact.get("version", "unversioned") if isinstance(artifact, dict) else "unversioned"
        )
        self.loaded = True

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        """Return raw model output. The caller decides actions; this never triggers them."""
        if not self.loaded:
            score = _stub_score(str(features.get("transaction_id", "unknown")))
            return {
                "score": score,
                "band": _band_for(score),
                "top_factors": [],
                "model_version": self.version,
                "calibrated": False,
                "fallback_used": True,
            }
        try:
            vector = _feature_vector(features, self.model)
            probs = self.model.predict_proba(vector) if hasattr(self.model, "predict_proba") else None
            score = float(probs[0][1]) if probs is not None else float(self.model.predict(vector)[0])
            score = max(0.0, min(1.0, score))
            return {
                "score": score,
                "band": _band_for(score),
                "top_factors": _top_factors(features),
                "model_version": self.version,
                "calibrated": False,  # no calibration demonstrated yet
                "fallback_used": False,
            }
        except Exception:
            score = _stub_score(str(features.get("transaction_id", "unknown")))
            return {
                "score": score,
                "band": _band_for(score),
                "top_factors": [],
                "model_version": f"{self.version}-error-stub",
                "calibrated": False,
                "fallback_used": True,
            }


def _feature_vector(features: dict[str, Any], model: Any) -> list[list[float]]:
    """Best-effort ordering by the model's ``feature_names_in_``."""
    names = getattr(model, "feature_names_in_", None)
    if names is not None:
        return [[float(features.get(name, 0.0)) for name in names]]
    keys = [k for k in features.keys() if isinstance(features[k], (int, float))]
    return [[float(features[k]) for k in keys]]


def _top_factors(features: dict[str, Any]) -> list[dict[str, Any]]:
    # With raw numeric features we only know names/values, not SHAP contributions.
    return [
        {"factor": key, "value": value, "contribution": None, "direction": "up"}
        for key, value in features.items()
        if isinstance(value, (int, float))
    ][:5]


def _stub_score(seed: str) -> float:
    total = sum(ord(ch) for ch in seed)
    return round((total % 91) / 100.0, 3)


def _band_for(score: float) -> str:
    if score >= 0.8:
        return "HIGH"
    if score >= 0.5:
        return "MEDIUM"
    return "LOW"