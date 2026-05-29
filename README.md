# Medical Desert France

Open-source MLOps project for predicting French commune-level medical-access risk. The
machine learning is intentionally simple so the repository can focus on reproducible data
workflows, model serving, dashboard data, and Kubernetes deployments across local servers,
AWS, GCP, and Azure.

## What This Project Demonstrates

- Public-data ingestion for commune metadata and medical-access indicators.
- Simple scikit-learn risk classification from tabular commune-level features.
- MLflow experiment tracking and model artifact logging.
- FastAPI prediction and dashboard API.
- PostgreSQL storage for commune metadata and dashboard-ready metrics.
- Lightweight dashboard UI.
- Docker images for the API, dashboard, training jobs, and local services.
- Kubernetes-first deployment with Helm.
- OpenTofu scaffolds for EKS, GKE, and AKS.

Primary public data sources:

- DREES APL healthcare-access indicators: <https://www.data.gouv.fr/datasets/laccessibilite-potentielle-localisee-apl/>
- INSEE geographic references: <https://www.insee.fr/fr/information/8740222>

## Local Python Workflow

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

Create tables, seed sample data, train a starter model, and run the API:

```bash
mdf migrate
mdf seed-db --data data/sample_communes.csv
mdf train --data data/sample_communes.csv --output models/model.joblib
uvicorn medical_desert_france.api:app --reload
```

Useful endpoints:

- `GET /health`
- `GET /model/info`
- `GET /communes`
- `GET /communes/{code}`
- `POST /predict`
- `GET /dashboard/summary`
- `GET /dashboard/regions`

Example prediction:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"commune_code":"23096"}'
```

## Deployment Model

The target deployment architecture is Kubernetes everywhere:

- Local server: k3s, k3d, kind, or Minikube.
- AWS: EKS.
- GCP: GKE.
- Azure: AKS.

The application layer is deployed with Helm. Cloud infrastructure is provisioned with
OpenTofu modules under `infra/opentofu`.

## Database

PostgreSQL stores application/dashboard data:

- Commune metadata.
- Precomputed dashboard metrics.
- Prediction records and model version references.

MLflow and object storage remain responsible for experiments and model artifacts.

## Development Checks

```bash
ruff check .
pytest
```

## License

MIT
