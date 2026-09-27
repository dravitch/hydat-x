# benchmark/splits/

Deux objets de découpage indépendants, matérialisés par M02 et non gelés.

## Split temporel (proposition)

```text
TRAIN ──> VALIDATION ──> TEST ──> HOLDOUT      (chronologique, sans interpénétration)
```

| Split | Bornes | Rôle |
|---|---|---|
| TRAIN | ≤ 2010 | entraînement |
| VALIDATION | 2011–2015 | réglage / sélection |
| TEST | 2016–2020 | évaluation finale du protocole (jamais réglée) |
| HOLDOUT | 2021–2025 | confrontation finale avec le candidat |

Artefact : `temporal/station-periods.csv`; manifeste et empreinte :
`temporal/manifest.json`. Une station peut apparaître dans plusieurs périodes : c'est voulu
pour l'évaluation temporelle, sans influence du futur sur le passé.

## Split géographique

Artefact : `geographic/stations.csv`; manifeste : `geographic/manifest.json`. Les régions
administratives complètes sont affectées par `SHA256(region) modulo 8` : le bucket 7 est
GEO-TEST. Résultat : 1 796 stations GEO-TRAIN et 321 GEO-TEST, avec des stations **et des
régions** strictement disjointes. Les régions de test sont AK, NL, NT et QC.

## Matériel d'audit disponible maintenant

- `evaluation/reports/DATA-AUDIT-001/temporal-coverage.parquet` (station × année, disponibilité
  par année) — base de calcul des bornes par date.
- `evaluation/reports/DATA-AUDIT-001/coverage.csv` (par station: première/dernière observation,
  couverture, missingness) — pour vérifier qu'aucune station ne déborde un split.
