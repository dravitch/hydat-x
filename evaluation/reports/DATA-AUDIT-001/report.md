# DATA-AUDIT-001 — rapport d'audit (auto-généré)

- release : **20260717** ; fichier : `Hydat.sqlite3`
- exécuté en lecture seule (ATTACH READ_ONLY)
- horodatage : 2026-09-24T03:40:20Z
- chiffres traçables aux requêtes SQL du script
---

## 1. Inventaire base

- **33 tables** ; lignes : 3,719,056.

- Détail colonnes/types/clés candidates : `tables.csv`.

- Relations : voir `docs/DATA-AUDIT-001.md` (schéma HYDAT).

## 2. Stations

- **8057** stations ; actives **2896** ; coordonnées **8057** ; superficie **7713** ; RHBN **314**.

- durée d'enregistrement : {'>30 ans': 2291, 'NA': 1579, '1-5 ans': 1344, '5-10 ans': 990, '20-30 ans': 698, '10-15 ans': 662, '15-20 ans': 493, '<1 an': 0}.

- par province : {'BC': 2324, 'ON': 1119, 'AB': 1104, 'QC': 1001, 'SK': 748, 'MB': 659, 'NT': 245, 'NL': 230, 'NB': 144, 'NS': 144, 'YT': 114, 'NU': 109, 'PE': 43, 'MT': 30, 'WA': 11, 'ND': 8, 'ME': 7, 'MN': 7, 'AK': 4, 'ID': 4, 'MI': 2}.

## 3. Couverture temporelle

- stations avec ≥1 jour de débit valide : **6464**.

- stations avec cellules mais **0 observation valide** (tous les jours 0.0 ou symboles non-D) : **14** — à exclure de la population exploitable (voir DATA-AUDIT-001).

- jours valides (total) : 49,548,861 ; médiane par station : 4,112.

- jours 0.0 sans symbole (ambigu) : 2,681,900 — voir HYDAT-DATA-QUALITY.md.

- couverture médiane (jours valides/registre) : 0.7991.

- `coverage.csv` (par station) ; `temporal-coverage.parquet` (station × année).

## 4. Qualité & missingness

- symboles sur jours : {'__NULL__': 39696508, 'B': 10157834, 'E': 2788490, 'A': 376961, ' ': 1161}.

- jours à **0.0** — par symbole : {'__NULL__': 2681900, 'B': 642659, 'E': 132049, 'A': 14003}.

→ 0.0 sans symbole : sémantique ambiguë dans la doc HYDAT ; comptée séparément, jamais supposée. Symbole `' '` (espace), 1161 cellules hors vocabulaire officiel (A/B/D/E/S), toutes valeurs non nulles (0 jour à 0.0) — documenté HYDAT-DATA-QUALITY.md.

- PRECISION_CODE (pics annuels) : {'NULL': 110785, '8': 68468, '9': 3470} ; FULL_MONTH (mois débit) : {'1': 1720863, '0': 59008}.

## 5. Distributions (débit journalier, m³/s)

- par station : `distributions.csv` (count/min/p01/p05/median/p95/p99/p999/max + n_est).

- distributions fortement asymétriques → quantiles robustes utilisés (voir summary.json).

- jours estimés (symbole E) retenus : comptés dans n_est, inclus dans les quantiles (documenté HYDAT-DATA-QUALITY.md).

## 6. Extrêmes annuels (pics)

- pics de type H (max) : **88,556** ; type L (min) : 22,229 ; stations concernées : 3546.

- pics H/année : min 1, médiane 515.5, max 1809 (période 1904–2025).

- relation pics vs série journalière : voir DATA-AUDIT-001.md (comparaison partielle station vs flux annuel max).

## 7. Exploration des targets — comparaison quantitative

- T1 (quantiles) , T3 (pics) , T4 (persistance N jours) : voir `target-events.csv` et `events/*.csv`.

- T2 (seuil absolu) : **aucun seuil officiel dans HYDAT** → HUMAN DECISION REQUIRED (documenté TARGET-DESIGN-001.md).

- Variantes 'whole' = future-informed (marquées) ; 'refhalf' = seuil sur 1re moitié (historical/reference) — §11 leakage.

## 8. Saisonnalité (target T1-q099-whole)

P(événement | jour) par mois : m1: 0.003818, m2: 0.003678, m3: 0.007806, m4: 0.023148, m5: 0.026578, m6: 0.022908, m7: 0.008892, m8: 0.002792, m9: 0.002135, m10: 0.002596, m11: 0.003506, m12: 0.003593

Définition P = jours-évt / jours-station valides (mois). cf. phase F mission — baseline descriptive, pas de ML.

---
## Queries
Les requêtes SQL (une par section) sont intégrées dans `scripts/audit_hydat.py`, reproduites dans `docs/DATA-AUDIT-001.md`.
