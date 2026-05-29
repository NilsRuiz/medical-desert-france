import pandas as pd

from medical_desert_france.ml.features import FEATURE_COLUMNS, build_training_frame


def test_build_training_frame_derives_risk_classes() -> None:
    frame = pd.DataFrame(
        [
            {"apl_score": 1.2, "population": 1000, "department_code": "23", "region_code": "75"},
            {"apl_score": 3.1, "population": 2000, "department_code": "59", "region_code": "32"},
            {"apl_score": 5.0, "population": 3000, "department_code": "75", "region_code": "11"},
        ]
    )

    features, target = build_training_frame(frame)

    assert list(features.columns) == FEATURE_COLUMNS
    assert target.tolist() == ["high", "medium", "low"]
