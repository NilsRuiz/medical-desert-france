# Data

This project is designed for public aggregate datasets only.

## Sources

- DREES APL healthcare-access indicators:
  <https://www.data.gouv.fr/datasets/laccessibilite-potentielle-localisee-apl/>
- INSEE geographic references:
  <https://www.insee.fr/fr/information/8740222>

## Expected Commune Table

The starter pipeline expects a CSV with these columns:

- `code`
- `name`
- `department_code`
- `department_name`
- `region_code`
- `region_name`
- `population`
- `apl_score`
- `latitude`
- `longitude`

`data/sample_communes.csv` provides a small development fixture. Real ingestion scripts can
replace it with downloaded public-data extracts while preserving this normalized schema.
