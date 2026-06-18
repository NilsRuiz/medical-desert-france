# API

## Health

```http
GET /health
```

Returns service status and environment name.

## Model Info

```http
GET /model/info
```

Returns model version, artifact path, load status, and expected feature names.

## Prediction

```http
POST /predict
```

Either send a `commune_code` already present in PostgreSQL:

```json
{"commune_code": "23096"}
```

Or send feature values directly:

```json
{
  "apl_score": 2.1,
  "population": 12889,
  "department_code": "23",
  "region_code": "75"
}
```

## Dashboard Data

```http
GET /communes
GET /communes/{code}
GET /dashboard/summary
GET /dashboard/regions
GET /dashboard/departments
```

`/dashboard/departments` returns department-level aggregates for the dashboard map:
commune count, population, average APL score, high-risk commune count, and risk class.
