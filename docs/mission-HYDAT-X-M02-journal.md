# Journal d’exécution — HYDAT-X M02

## Statut

`READY_FOR_M03_REAUDIT`

Mission source : `docs/mission-HYDAT-X-M02-reconstruire-reference-v01.md`

## Baseline de départ

- Date de démarrage : 2026-09-27 (America/Toronto)
- Branche : `main`
- Commit de départ : `561e630d60b70bc697067e64a9c90aebeb0e6b05`
- Base HYDAT brute : `data/raw/hydat/20260717/sqlite/Hydat.sqlite3`
- SHA-256 de la base brute : `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517`
- État initial du worktree : non propre; les modifications et fichiers non suivis préexistants sont conservés.
- Audit historique protégé : `scripts/audit_hydat.py` et `evaluation/reports/DATA-AUDIT-001/` ne seront pas modifiés.
- Correctif F01 protégé : `evaluation/reports/DATA-AUDIT-001-F01FIX/` ne sera pas modifié.
- Gel, commit et tag : hors périmètre de M02.

## Décisions d’exécution

- La nouvelle chaîne sera implémentée séparément de la chaîne historique.
- Tout cache de la nouvelle chaîne devra posséder un manifeste conforme et une identité vérifiable; l’absence ou la divergence du manifeste entraînera un refus fermé puis une régénération explicite.
- Les artefacts de M02 seront écrits sous `evaluation/reports/DATA-AUDIT-002/` et dans les répertoires `benchmark/` prévus par la mission.

## Chronologie

- 2026-09-27 — Baseline capturée; mission passée à `ACTIVE`.
- 2026-09-27 — Baseline M01 exécutée : 5 tests réussis.
- 2026-09-27 — Nouveau cache canonique généré depuis la base brute; manifeste d'identité écrit.
- 2026-09-27 — DATA-AUDIT-002 final régénéré en 114,769 s avec le code destiné au commit.
- 2026-09-27 — Reproduction finale avec cache validé en 37,286 s; action `accepted`.
- 2026-09-27 — Définitions des quatre cibles, deux splits, décisions et rapports documentés.
- 2026-09-27 — Suite renforcée : 28 tests réussis; manifests, empreintes et source brute vérifiés.

## Résultats

| Cible | Événements | Stations | Év./station | Médiane | Maximum | `span != dur` |
|---|---:|---:|---:|---:|---:|---:|
| T1-q095-refhalf | 92 634 | 2 092 | 44,280 | 2 j | 678 j | 0 |
| T1-q099-refhalf | 32 819 | 2 044 | 16,056 | 2 j | 663 j | 0 |
| T3-peak-q09-refhalf | 3 442 | 1 342 | 2,565 | 1 j | 1 j | 0 |
| T4-q099-N5-refhalf | 6 708 | 1 618 | 4,146 | 8 j | 663 j | 0 |

Splits : TRACK-TEMPORAL couvre 6 464 stations; TRACK-GEOGRAPHIC comprend 1 796 stations
GEO-TRAIN et 321 GEO-TEST, sans chevauchement de station ni de région administrative.

## Comparaison de contrôle

| Audit / cible | Événements | Violations | Stations | Év./station | Médiane | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| DATA-AUDIT-001 Q95 | 238 799 | 564 | 5 840 | 40,890 | 3 | 3 663 |
| DATA-AUDIT-001-F01FIX Q95 | 240 067 | 0 | 5 840 | 41,107 | 3 | 3 663 |
| DATA-AUDIT-002 Q95 | 92 634 | 0 | 2 092 | 44,280 | 2 | 678 |
| DATA-AUDIT-001 Q99 | 85 076 | 211 | 5 336 | 15,944 | 2 | 3 663 |
| DATA-AUDIT-001-F01FIX Q99 | 85 629 | 0 | 5 336 | 16,047 | 2 | 3 663 |
| DATA-AUDIT-002 Q99 | 32 819 | 0 | 2 044 | 16,056 | 2 | 663 |

DATA-AUDIT-002 a une autre fenêtre d'information : seuil sur TRAIN fixe, puis application
2011–2025. Les différences de volumes ne doivent donc pas être interprétées comme une simple
variation produite par F01.

## Vérifications

- `nix develop` → environnement du projet chargé lors de chaque exécution.
- `nix develop -c python -m pytest -q` → **28 passed**.
- `nix develop -c python scripts/audit_reference.py` → **succès**, cache accepté à la seconde exécution.
- `git diff --check` → **succès**.
- `scripts/reproduce_f01_span.py` → DATA-AUDIT-001 : **564 / 211** violations;
  DATA-AUDIT-001-F01FIX : **0 / 0**.
- Base brute après exécution → SHA-256 identique à la baseline.
- Quatre PDF ECCC → chemins résolus et SHA-256 conformes.
- DATA-AUDIT-001-F01FIX → empreintes des deux artefacts inchangées.
- `scripts/audit_hydat.py` historique → SHA-256 `8a66610c…c7e`, identique au manifeste F01FIX.
- DATA-AUDIT-002 → 22 artefacts importants inventoriés avec taille et SHA-256.
- YAML/JSON M02 → analyse syntaxique réussie.

## Findings F-02 à F-06

| Finding | Résolution et preuve |
|---|---|
| F-02 | Couverture station–année avec population, observé brut, numérateur, dénominateur, classe continue/saisonnière et seuil 80 % dans `coverage/station-year-coverage.csv`. |
| F-03 | `scripts/cache_manager.py` refuse cache/manifeste/identité divergents; tests source, code, manifeste absent et cache valide. |
| F-04 | Quatre familles réellement matérialisées avec rôle, seuils, périodes, comptes, durée, saisonnalité, couverture et risque de fuite dans le manifeste. |
| F-05 | Quatre PDF ECCC réels retrouvés sous `documentation/`; chemins corrigés et quatre empreintes vérifiées. |
| F-06 | TRACK-TEMPORAL strict par dates et TRACK-GEOGRAPHIC par régions entières, avec manifests, stations, dates, hashes et tests anti-fuite. |

Les décisions D1–D6 sont appliquées et explicitées dans `docs/DECISIONS-M02.md`. Le benchmark
primaire est `VERY_HIGH_FLOW_EVENT` / `T1-q095-refhalf`; Q99, T3 et T4 conservent leurs rôles
de challenge distincts. Les horizons autorisés restent 1, 3 et 7 jours.

## Anomalies rencontrées

- DuckDB réserve les identifiants `value`, `year` et `month`; les alias de la nouvelle chaîne
  ont été rendus explicites. Les échecs intermédiaires n'ont modifié ni la base brute ni les
  audits antérieurs.
- Une tentative de vérification Nix a été bloquée par le socket du bac à sable; la même
  vérification a ensuite réussi dans l'environnement autorisé.

## Anomalies et limites restantes pour M03

- Les plus longues séquences continues atteignent 678 jours (Q95) et 663 jours (Q99/N5).
  Elles respectent `span == dur` et les frontières de split, mais leur plausibilité
  hydrologique doit être contre-vérifiée.
- Six événements T3 n'ont pas de mois renseigné dans HYDAT; ils sont publiés sous `UNKNOWN`,
  jamais imputés en janvier.
- Les calendriers saisonniers présentent 22 377 jours au-delà du dénominateur normatif 217;
  ils sont conservés dans une colonne distincte et le ratio est borné à 1.

## Clôture M02

Les exigences de M02 sont implémentées et vérifiées. Le protocole reste `draft`, les splits
restent `reference-not-frozen`, et aucun commit, tag ou gel n'a été effectué. Prochaine étape :
ré-audit indépendant M03.
