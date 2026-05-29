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


@app.get("/dashboard/summary", response_model=list[DashboardMetricRead])
def dashboard_summary(session: Session = Depends(get_session)):
    statement = select(DashboardMetric).where(DashboardMetric.scope == "national")
    return session.scalars(statement).all()


@app.get("/dashboard/regions", response_model=list[DashboardMetricRead])
def dashboard_regions(session: Session = Depends(get_session)):
    statement = select(DashboardMetric).where(DashboardMetric.scope == "region").order_by(DashboardMetric.label)
    return session.scalars(statement).all()
