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
- Department-level dashboard map colored by medical-access risk.
- Docker images for the API, dashboard, training jobs, and local services.
- Kubernetes-first deployment with Helm.
- OpenTofu scaffolds for EKS, GKE, and AKS.

Primary public data sources:

- DREES APL healthcare-access indicators: <https://www.data.gouv.fr/datasets/laccessibilite-potentielle-localisee-apl/>
- INSEE geographic references: <https://www.insee.fr/fr/information/8740222>

## Run Locally With Docker Compose

This is the recommended way to run the full local stack. It starts PostgreSQL, MLflow,
the FastAPI backend, the dashboard, and the seed-data job.

```bash
docker compose up --build
```

Open:

- Dashboard: <http://localhost:8080>
- API health: <http://localhost:8000/health>
- Dashboard API proxy: <http://localhost:8080/api/health>
- MLflow: <http://localhost:5000>

Useful checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8080/api/health
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"commune_code":"23096"}'
curl http://localhost:8000/dashboard/departments
```

Stop the stack:

```bash
docker compose down
```

Reset Docker volumes, including PostgreSQL and MLflow data:

```bash
docker compose down -v
docker compose up --build
```

## Local Python Workflow

Use this workflow when running the Python API directly on your host, without Docker
Compose. The Docker Compose database hostname is `postgres`, but that name only exists
inside the Compose network. For host-local development, use SQLite or a PostgreSQL URL
with `localhost`. MLflow also uses a local SQLite backend in this mode.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.local.example .env
```

You can then use the Makefile workflow:

```bash
make migrate
make seed
make train
make api
```

Or run the commands directly:

```bash
mdf migrate
mdf seed-db --data data/sample_communes.csv
mdf train --data data/sample_communes.csv --output local_models/model.joblib
uvicorn medical_desert_france.api:app --reload
```

The local MLflow tracking database is `mlflow.db`, configured through:

```env
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

If you prefer a host PostgreSQL database, start PostgreSQL first and set:

```env
DATABASE_URL=postgresql+psycopg://mdf:mdf@localhost:5432/mdf
```

## Dashboard And Map

The dashboard includes commune search, prediction display, summary metrics, and a
department-level risk map. The map uses `GET /dashboard/departments` and the local
GeoJSON asset at `dashboard/assets/departments.geojson`.

The current map asset is intentionally small and covers the sample departments in
`data/sample_communes.csv`: `13`, `23`, `48`, `59`, and `75`. It can be replaced later
with a full simplified French departments GeoJSON while keeping the same API contract.

Useful endpoints:

- `GET /health`
- `GET /model/info`
- `GET /communes`
- `GET /communes/{code}`
- `POST /predict`
- `GET /dashboard/summary`
- `GET /dashboard/regions`
- `GET /dashboard/departments`

Example prediction:

```bash
curl -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{"commune_code":"23096"}'
```

## Troubleshooting

If the dashboard container logs this error:

```text
host not found in upstream "api"
```

rebuild the dashboard image after pulling the latest config:

```bash
docker compose down
docker compose up --build
```

The dashboard Nginx config uses Docker's embedded DNS resolver so the API service is
resolved at request time, not when Nginx starts.

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
