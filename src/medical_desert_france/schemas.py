from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    environment: str


class ModelInfo(BaseModel):
    model_version: str
    artifact_path: str
    model_loaded: bool
    features: list[str]


class PredictionRequest(BaseModel):
    commune_code: str | None = None
    apl_score: float | None = Field(default=None, ge=0)
    population: int | None = Field(default=None, ge=0)
    department_code: str | None = None
    region_code: str | None = None


class PredictionResponse(BaseModel):
    commune_code: str | None
    risk_class: str
    risk_score: float
    model_version: str


class CommuneRead(BaseModel):
    code: str
    name: str
    department_code: str | None = None
    department_name: str | None = None
    region_code: str | None = None
    region_name: str | None = None
    population: int | None = None
    apl_score: float | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class DashboardMetricRead(BaseModel):
    scope: str
    scope_key: str
    label: str
    metric_name: str
    metric_value: float
    model_version: str
    computed_at: datetime

    model_config = {"from_attributes": True}


class DepartmentDashboardRead(BaseModel):
    department_code: str
    department_name: str
    region_code: str | None = None
    region_name: str | None = None
    commune_count: int
    population: int
    avg_apl_score: float | None = None
    high_risk_communes: int
    risk_class: str
