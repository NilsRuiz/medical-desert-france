from pathlib import Path

import joblib
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from medical_desert_france.config import get_settings
from medical_desert_france.ml.features import FEATURE_COLUMNS, build_training_frame


def train_model(data_path: str, output_path: str = "local_models/model.joblib") -> dict[str, float | str]:
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    frame = pd.read_csv(data_path)
    x, y = build_training_frame(frame)

    stratify = y if y.nunique() > 1 and y.value_counts().min() > 1 else None
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    pipeline = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")),
        ]
    )

    with mlflow.start_run(run_name="medical-desert-risk"):
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        mlflow.log_param("features", ",".join(FEATURE_COLUMNS))
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(pipeline, artifact_path="model")
        mlflow.log_text(classification_report(y_test, predictions), "classification_report.txt")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": pipeline, "features": FEATURE_COLUMNS}, output)
    return {"accuracy": float(accuracy), "artifact_path": str(output)}
