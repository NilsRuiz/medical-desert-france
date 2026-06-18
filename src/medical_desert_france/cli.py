import argparse

import pandas as pd
from sqlalchemy import select

from medical_desert_france.db import Base, SessionLocal, engine
from medical_desert_france.ml.train import train_model
from medical_desert_france.models import Commune, DashboardMetric


def migrate() -> None:
    Base.metadata.create_all(bind=engine)


def upsert_dashboard_metric(
    session,
    *,
    scope: str,
    scope_key: str,
    label: str,
    metric_name: str,
    metric_value: float,
    model_version: str,
) -> None:
    statement = select(DashboardMetric).where(
        DashboardMetric.scope == scope,
        DashboardMetric.scope_key == scope_key,
        DashboardMetric.metric_name == metric_name,
        DashboardMetric.model_version == model_version,
    )
    metric = session.scalar(statement)
    if metric is None:
        session.add(
            DashboardMetric(
                scope=scope,
                scope_key=scope_key,
                label=label,
                metric_name=metric_name,
                metric_value=metric_value,
                model_version=model_version,
            )
        )
        return

    metric.label = label
    metric.metric_value = metric_value


def seed_db(data_path: str) -> None:
    frame = pd.read_csv(data_path).fillna("")
    with SessionLocal() as session:
        for row in frame.to_dict(orient="records"):
            commune = Commune(
                code=str(row["code"]),
                name=str(row["name"]),
                department_code=str(row.get("department_code") or ""),
                department_name=str(row.get("department_name") or ""),
                region_code=str(row.get("region_code") or ""),
                region_name=str(row.get("region_name") or ""),
                population=int(row["population"]) if row.get("population") != "" else None,
                apl_score=float(row["apl_score"]) if row.get("apl_score") != "" else None,
                latitude=float(row["latitude"]) if row.get("latitude") != "" else None,
                longitude=float(row["longitude"]) if row.get("longitude") != "" else None,
            )
            session.merge(commune)
        session.commit()

        total = session.query(Commune).count()
        high_risk = session.query(Commune).filter(Commune.apl_score < 2.5).count()
        upsert_dashboard_metric(
            session,
            scope="national",
            scope_key="FR",
            label="France",
            metric_name="communes",
            metric_value=float(total),
            model_version="seed",
        )
        upsert_dashboard_metric(
            session,
            scope="national",
            scope_key="FR",
            label="France",
            metric_name="high_risk_communes",
            metric_value=float(high_risk),
            model_version="seed",
        )
        session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(prog="mdf")
    subparsers = parser.add_subparsers(dest="command", required=True)
    train_parser = subparsers.add_parser("train")
    train_parser.add_argument("--data", required=True)
    train_parser.add_argument("--output", default="local_models/model.joblib")
    seed_parser = subparsers.add_parser("seed-db")
    seed_parser.add_argument("--data", required=True)
    subparsers.add_parser("migrate")
    args = parser.parse_args()

    if args.command == "train":
        print(train_model(args.data, args.output))
    elif args.command == "seed-db":
        migrate()
        seed_db(args.data)
    elif args.command == "migrate":
        migrate()


if __name__ == "__main__":
    main()
