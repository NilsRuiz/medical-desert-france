.PHONY: install test lint migrate seed train api docker-build compose-up compose-down k8s-local

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest

lint:
	ruff check .

migrate:
	mdf migrate

seed:
	mdf seed-db --data data/sample_communes.csv

train:
	mdf train --data data/sample_communes.csv --output models/model.joblib

api:
	uvicorn medical_desert_france.api:app --reload

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
