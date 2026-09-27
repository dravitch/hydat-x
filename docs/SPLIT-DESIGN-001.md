# Split design 001

Statut : **reference-not-frozen** — prêt pour ré-audit M03.

## TRACK-TEMPORAL-v1

| Partition | Dates |
|---|---|
| TRAIN | jusqu'au 2010-12-31 inclus |
| VALIDATION | 2011-01-01 — 2015-12-31 |
| TEST | 2016-01-01 — 2020-12-31 |
| HOLDOUT | 2021-01-01 — 2025-12-31 |

Le split est effectué par date avant le calcul des seuils. Les seuils sont figés sur TRAIN.
Une même station peut être présente dans plusieurs partitions temporelles; aucune observation
postérieure à 2010 n'entre dans la calibration. Artefacts et empreintes :
`benchmark/splits/temporal/`.

## TRACK-GEOGRAPHIC-v1

Population : stations possédant au moins une observation valide dans TRAIN et une en
2011–2025. La séparation spatiale utilise la province, le territoire ou l'État HYDAT :
`SHA256(PROV_TERR_STATE_LOC) modulo 8`, bucket 7 en GEO-TEST. Les régions AK, NL, NT et QC
sont entièrement réservées au test; les 17 autres régions sont réservées au train.
Résultat : 1 796 / 321 stations, sans chevauchement de station ni de région.
Artefacts : `benchmark/splits/geographic/`.

Les deux tracks répondent à des questions différentes et ne doivent pas être confondus :
généralisation dans le temps versus généralisation à des stations jamais vues.
