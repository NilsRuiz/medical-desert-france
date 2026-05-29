import pandas as pd

FEATURE_COLUMNS = ["apl_score", "population", "department_code_numeric", "region_code_numeric"]
RISK_LABELS = ["low", "medium", "high"]


def normalize_commune_frame(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["department_code_numeric"] = pd.to_numeric(data.get("department_code"), errors="coerce")
    data["region_code_numeric"] = pd.to_numeric(data.get("region_code"), errors="coerce")
    for column in ["apl_score", "population", "department_code_numeric", "region_code_numeric"]:
        data[column] = pd.to_numeric(data.get(column), errors="coerce").fillna(0)
    return data


def build_training_frame(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    data = normalize_commune_frame(frame)
    if "risk_class" in data:
        target = data["risk_class"]
    else:
        target = pd.cut(
            data["apl_score"],
            bins=[-0.01, 2.5, 4.0, float("inf")],
            labels=["high", "medium", "low"],
        ).astype(str)
    return data[FEATURE_COLUMNS], target


def build_prediction_frame(payload: dict) -> pd.DataFrame:
    data = pd.DataFrame([payload])
    return normalize_commune_frame(data)[FEATURE_COLUMNS]
