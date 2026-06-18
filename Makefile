PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python; fi)
UVICORN ?= $(shell if [ -x .venv/bin/uvicorn ]; then echo .venv/bin/uvicorn; else echo uvicorn; fi)
MDF = PYTHONPATH=src $(PYTHON) -m medical_desert_france.cli

.PHONY: install test lint env-local local-init migrate seed train local-run local-reset postgres-local-up postgres-local-down api docker-build compose-up compose-down k8s-local

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	ruff check .

env-local:
	cp .env.local.example .env

local-init: install env-local

migrate:
	$(MDF) migrate

seed:
	$(MDF) seed-db --data data/sample_communes.csv

train:
	$(MDF) train --data data/sample_communes.csv --output local_models/model.joblib

local-run: migrate seed train api

local-reset: env-local
	rm -f local.db mlflow.db
	rm -rf local_models
	$(MAKE) local-run

postgres-local-up:
	docker run --name mdf-postgres -e POSTGRES_USER=mdf -e POSTGRES_PASSWORD=mdf -e POSTGRES_DB=mdf -p 5432:5432 -d postgres:16-alpine

postgres-local-down:
	docker stop mdf-postgres || true
	docker rm mdf-postgres || true

api:
	PYTHONPATH=src $(UVICORN) medical_desert_france.api:app --reload

docker-build:
	docker build -f Dockerfile.api -t medical-desert-api:local .
	docker build -f Dockerfile.dashboard -t medical-desert-dashboard:local .

compose-up:
	docker compose up --build

compose-down:
	docker compose down

k8s-local:
	helm dependency update deploy/helm
	helm upgrade --install medical-desert deploy/helm -f deploy/helm/values-local.yaml --namespace medical-desert --create-namespace
