# Architecture

## Components

- Data/ML package: loads commune-level data, builds features, trains a simple classifier,
  and writes model artifacts.
- API: FastAPI service for predictions, commune lookup, model info, and dashboard data.
- Dashboard: browser UI that consumes API endpoints.
- PostgreSQL: stores commune metadata, dashboard metrics, and prediction records.
- MLflow: tracks experiments and model artifacts.
- Kubernetes: standard runtime across local server, EKS, GKE, and AKS.

## Data Flow

1. Public data is downloaded and normalized into commune-level tabular data.
2. The training pipeline derives risk classes from APL scores and trains a scikit-learn model.
3. Model metadata and artifacts are logged to MLflow.
4. Commune metadata and dashboard aggregates are loaded into PostgreSQL.
5. The API serves commune data from PostgreSQL and predictions from the model artifact.
6. The dashboard renders summary metrics and commune-level prediction results.

## Deployment

OpenTofu provisions Kubernetes clusters and cloud prerequisites. Helm deploys the
application stack to every target environment.
