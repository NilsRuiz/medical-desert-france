from functools import lru_cache
from pathlib import Path

import joblib

from medical_desert_france.config import get_settings
from medical_desert_france.ml.features import FEATURE_COLUMNS, build_prediction_frame


@lru_cache
def load_model():
    path = Path(get_settings().model_artifact_path)
    if not path.exists():
        return None
    return joblib.load(path)


def predict_risk(payload: dict) -> tuple[str, float]:
    bundle = load_model()
    if bundle is None:
        apl_score = float(payload.get("apl_score") or 0)
        if apl_score < 2.5:
            return "high", 0.75
        if apl_score < 4.0:
            return "medium", 0.55
        return "low", 0.70

    model = bundle["model"]
    frame = build_prediction_frame(payload)
    risk_class = str(model.predict(frame)[0])
    score = 1.0
    if hasattr(model, "predict_proba"):
        score = float(model.predict_proba(frame).max(axis=1)[0])
    return risk_class, score


def model_loaded() -> bool:
    return load_model() is not None


def model_features() -> list[str]:
    bundle = load_model()
    if bundle is None:
        return FEATURE_COLUMNS
    return list(bundle.get("features", FEATURE_COLUMNS))
