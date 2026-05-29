from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medical_desert_france.db import Base


class Commune(Base):
    __tablename__ = "communes"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    department_code: Mapped[str | None] = mapped_column(String(4), index=True)
    department_name: Mapped[str | None] = mapped_column(String(255))
    region_code: Mapped[str | None] = mapped_column(String(4), index=True)
    region_name: Mapped[str | None] = mapped_column(String(255), index=True)
    population: Mapped[int | None] = mapped_column(Integer)
    apl_score: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    predictions: Mapped[list["CommunePrediction"]] = relationship(back_populates="commune")


class CommunePrediction(Base):
    __tablename__ = "commune_predictions"
    __table_args__ = (
        UniqueConstraint("commune_code", "model_version", name="uq_prediction_commune_model"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    commune_code: Mapped[str] = mapped_column(ForeignKey("communes.code"), index=True)
    model_version: Mapped[str] = mapped_column(String(128), index=True)
    risk_class: Mapped[str] = mapped_column(String(32), index=True)
    risk_score: Mapped[float] = mapped_column(Float)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    commune: Mapped[Commune] = relationship(back_populates="predictions")


class DashboardMetric(Base):
    __tablename__ = "dashboard_metrics"
    __table_args__ = (
        UniqueConstraint("scope", "scope_key", "metric_name", "model_version", name="uq_dashboard_metric"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(String(32), index=True)
    scope_key: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(255))
    metric_name: Mapped[str] = mapped_column(String(128), index=True)
    metric_value: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(128), index=True)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
