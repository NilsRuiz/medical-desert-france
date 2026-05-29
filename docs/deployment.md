# Deployment

This repository includes a Kubernetes-first scaffold for the API, dashboard, PostgreSQL, MLflow, and one-off MLOps jobs.

## Helm

Render the chart locally:

```bash
helm dependency update deploy/helm
helm template mdf deploy/helm
```

Install into a cluster:

```bash
helm upgrade --install mdf deploy/helm --namespace medical-desert --create-namespace
```

Before production use, override image repositories, tags, ingress hosts, credentials, and storage classes in a values file. The chart can use the bundled Bitnami PostgreSQL dependency for development, or an external database by setting `postgresql.enabled=false`, `database.host`, and database credentials, or by providing `database.existingSecret`.

The migration job runs as a Helm hook by default. Seed and training jobs are rendered as normal Kubernetes Jobs and can be disabled with `jobs.seed.enabled=false` and `jobs.training.enabled=false`.

## OpenTofu

Cloud scaffolds live under `infra/opentofu`:

```bash
cd infra/opentofu/examples/eks
tofu init
tofu plan
```

Equivalent examples exist for GKE and AKS. The modules intentionally assume existing networking and leave production decisions as TODOs: private endpoints, managed PostgreSQL, registry integration, workload identity, secrets, autoscaling, observability, and cluster add-ons.

