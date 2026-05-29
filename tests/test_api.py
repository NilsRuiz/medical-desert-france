from fastapi.testclient import TestClient

from medical_desert_france.api import app
from medical_desert_france.db import Base, build_engine, get_session
from medical_desert_france.models import Commune, DashboardMetric


def test_api_health_and_commune_prediction() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            Commune.__table__.insert(),
            [
                {
                    "code": "23096",
                    "name": "Gueret",
                    "department_code": "23",
                    "department_name": "Creuse",
                    "region_code": "75",
                    "region_name": "Nouvelle-Aquitaine",
                    "population": 12889,
                    "apl_score": 2.1,
                    "latitude": 46.17,
                    "longitude": 1.87,
                }
            ],
        )
        connection.execute(
            DashboardMetric.__table__.insert(),
            [
                {
                    "scope": "national",
                    "scope_key": "FR",
                    "label": "France",
                    "metric_name": "communes",
                    "metric_value": 1,
                    "model_version": "test",
                }
            ],
        )

    def override_session():
        from sqlalchemy.orm import Session

        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/communes/23096").json()["name"] == "Gueret"
    prediction = client.post("/predict", json={"commune_code": "23096"}).json()
    assert prediction["risk_class"] == "high"
    assert client.get("/dashboard/summary").json()[0]["metric_name"] == "communes"

    app.dependency_overrides.clear()
