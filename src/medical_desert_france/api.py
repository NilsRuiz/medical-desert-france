from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from medical_desert_france.config import get_settings
from medical_desert_france.db import get_session
from medical_desert_france.ml.predict import model_features, model_loaded, predict_risk
from medical_desert_france.models import Commune, DashboardMetric
from medical_desert_france.schemas import (
    CommuneRead,
    DashboardMetricRead,
    DepartmentDashboardRead,
    HealthResponse,
    ModelInfo,
    PredictionRequest,
    PredictionResponse,
)

class StripApiPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http" and scope.get("path", "").startswith("/api"):
            scope = dict(scope)
            path = scope["path"][4:]
            scope["path"] = path or "/"
            scope["root_path"] = f'{scope.get("root_path", "")}/api'
        await self.app(scope, receive, send)


settings = get_settings()
app = FastAPI(title="Medical Desert France API", version="0.1.0")
app.add_middleware(StripApiPrefixMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(environment=settings.app_env)


@app.get("/model/info", response_model=ModelInfo)
def model_info() -> ModelInfo:
    return ModelInfo(
        model_version=settings.model_version,
        artifact_path=settings.model_artifact_path,
        model_loaded=model_loaded(),
        features=model_features(),
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, session: Session = Depends(get_session)) -> PredictionResponse:
    payload = request.model_dump()
    commune_code = request.commune_code
    if commune_code:
        commune = session.get(Commune, commune_code)
        if commune is None:
            raise HTTPException(status_code=404, detail="Commune not found")
        payload |= {
            "apl_score": commune.apl_score,
            "population": commune.population,
            "department_code": commune.department_code,
            "region_code": commune.region_code,
        }
    risk_class, risk_score = predict_risk(payload)
    return PredictionResponse(
        commune_code=commune_code,
        risk_class=risk_class,
        risk_score=risk_score,
        model_version=settings.model_version,
    )


@app.get("/communes", response_model=list[CommuneRead])
def list_communes(q: str | None = None, limit: int = 50, session: Session = Depends(get_session)):
    statement = select(Commune).order_by(Commune.name).limit(min(limit, 200))
    if q:
        statement = select(Commune).where(Commune.name.ilike(f"%{q}%")).order_by(Commune.name).limit(min(limit, 200))
    return session.scalars(statement).all()


@app.get("/communes/{code}", response_model=CommuneRead)
def get_commune(code: str, session: Session = Depends(get_session)):
    commune = session.get(Commune, code)
    if commune is None:
        raise HTTPException(status_code=404, detail="Commune not found")
    return commune


def department_risk_class(avg_apl_score: float | None, high_risk_share: float) -> str:
    if avg_apl_score is None:
        return "unknown"
    if avg_apl_score < 2.5 or high_risk_share >= 0.5:
        return "high"
    if avg_apl_score < 4.0 or high_risk_share > 0:
        return "medium"
    return "low"


@app.get("/dashboard/departments", response_model=list[DepartmentDashboardRead])
def dashboard_departments(session: Session = Depends(get_session)) -> list[DepartmentDashboardRead]:
    communes = session.scalars(select(Commune).order_by(Commune.department_code, Commune.name)).all()
    grouped: dict[str, list[Commune]] = {}
    for commune in communes:
        if commune.department_code:
            grouped.setdefault(commune.department_code, []).append(commune)

    departments: list[DepartmentDashboardRead] = []
    for department_code, rows in grouped.items():
        apl_values = [row.apl_score for row in rows if row.apl_score is not None]
        avg_apl = sum(apl_values) / len(apl_values) if apl_values else None
        high_risk = sum(1 for row in rows if row.apl_score is not None and row.apl_score < 2.5)
        population = sum(row.population or 0 for row in rows)
        departments.append(
            DepartmentDashboardRead(
                department_code=department_code,
                department_name=rows[0].department_name or department_code,
                region_code=rows[0].region_code,
                region_name=rows[0].region_name,
                commune_count=len(rows),
                population=population,
                avg_apl_score=round(avg_apl, 2) if avg_apl is not None else None,
                high_risk_communes=high_risk,
                risk_class=department_risk_class(avg_apl, high_risk / len(rows)),
            )
        )
    return sorted(departments, key=lambda item: item.department_name)


@app.get("/dashboard/summary", response_model=list[DashboardMetricRead])
def dashboard_summary(session: Session = Depends(get_session)):
    statement = select(DashboardMetric).where(DashboardMetric.scope == "national")
    return session.scalars(statement).all()


@app.get("/dashboard/regions", response_model=list[DashboardMetricRead])
def dashboard_regions(session: Session = Depends(get_session)):
    statement = select(DashboardMetric).where(DashboardMetric.scope == "region").order_by(DashboardMetric.label)
    return session.scalars(statement).all()
