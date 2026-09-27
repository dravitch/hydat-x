# HYDAT-X Reference Protocol — v0.2 (DRAFT)

| Champ | Valeur |
|---|---|
| Version | 0.2-draft |
| Date draft | 2026-09-27 |
| Statut | **draft — READY_FOR_M03_REAUDIT**, non gelé |
| Projet | 83-HYDAT-X (autonome) |
| Remplaçant | v0.1 (seuils chiffrés arbitrés ci-dessous, à confirmer au gel) |
| Sources | `docs/SOURCES.md`, SCHEMA LIV01 rc3 §9 (T1/T2/T3), diagnostic agent-5, v0.1, audits DATA-AUDIT-001 |

Une fois **gelé**, ce document est l'unique référentiel expérimental. Aucun changement de règle
pour « accommoder un modèle » : le candidat entre comme objet testé contre le référentiel. Rien
dans ce document ne suppose l'accès au code, aux données préparées ni aux métriques de l'équipe
candidate.

---

## 1. Périmètre

Plateforme de contre-expertise reproductible du prototype d'alerte aux inondations.

Revendication de référence (à tester, jamais admise) :
> 15 ans de données HYDAT, 2 000+ stations, AUC-ROC 0,95 sur données inédites.

Objectifs : **REPRODUCE**, **CHALLENGE**, **COMPARE** (baselines). Hors périmètre : chaîne T1
(destinataire/décision/valeur) et comparateur NSRPS/GEM-Hydro (opérés par SCHEMA rc3 T1 ; R9) —
HYDAT-X fournit la matière empirique T2/T3 sans jugement politique.

## 2. Datasets — gel de la source de vérité

- **HYDAT_RAW** : `data/raw/hydat/20260717/` — immuable, manifeste SHA-256
  (`registry/datasets/hydat-reference-20260717.yaml`), 33 tables sqlite.
- **HYDAT_CANONICAL v2** : `data/canonical/hydat/20260717/daily-flows-v2.parquet`, cache à
  identité forte lié à la source, au code, aux paramètres et au schéma par
  `registry/datasets/hydat-daily-flows-v2-cache.json`.
- Aucune transformation destructive ; toute couche dérivée est versionnée avec son manifeste.

## 3. Population et couverture

| Objet | Population M02 | Règle |
|---|---|---|
| seuil journalier | station avec ≥1 jour valide dans TRAIN | `value>0 OR symbol='D'` |
| évaluation cible | observations valides 2011–2025 possédant un seuil TRAIN | aucune durée minimale de registre inventée |
| track géographique | ≥1 jour valide dans TRAIN et ≥1 en 2011–2025 | régions administratives entièrement disjointes |
| qualité | toutes les stations-années observées ≤2025 | flags B/E/A conservés et comptés |

La complétude 80 % est **publiée comme attribut**, pas utilisée comme filtre silencieux :
292/365 jours (293/366 en année bissextile) pour une station continue et 174/217 pour une
station saisonnière explicitement classée. Voir `docs/HYDAT-DATA-QUALITY-002.md`.

## 4. Période et découpage (=== réponse à Q4 ===)

Séparation **temporelle stricte**, jamais `train_test_split(random_state=42)` :

```text
TRAIN ──> VALIDATION ──> TEST ──> HOLDOUT   (chronologique, sans interpénétration)
```

| Split | Rôle | Bornes M02 |
|---|---|---|
| TRAIN | construction des seuils / entraînement | ≤ 2010-12-31 |
| VALIDATION | réglage/sélection | 2011-01-01 — 2015-12-31 |
| TEST | évaluation finale protocole | 2016-01-01 — 2020-12-31 |
| HOLDOUT | confrontation finale candidat | 2021-01-01 — 2025-12-31 |

**Découpage temporel M02 (non gelé)** : splits **par date** — ≤2010 TRAIN, 2011–2015
VALIDATION, 2016–2020 TEST, 2021–2025 HOLDOUT. **Découpage géographique** indépendant :
stations et régions GEO-TRAIN/GEO-TEST disjointes (§SPLIT-DESIGN-001).

Règle : **aucun jour de TEST/HOLDOUT dans une fenêtre de contexte de TRAIN/VALIDATION** ;
aucune normalisation/imputation/création de variable calculée sur l'ensemble amont avant
découpage. Le split temporel se fait **avant** tout calcul de quantile (fuite §7).

## 5. Observation & missingness

- Observation : débit moyen journalier (m³/s) — cellule publique, champ `value` par jour.
- Missing data : politique §3r3 (`valid ⇔ value>0 OR symbol='D'`) ; jours 0.0 sans symbole =
  **non-observations** comptés `n_zero_blank` (2,68 M j — HDR D1) ; aucune imputation.
- Quality flags : §3 #5 + rapport stratifié par symbole (jamais de suppression silencieuse).

## 6. Targets (=== réponse à Q2 ===)

Cibles M02 : **`benchmark/targets/*.yaml`** + `docs/TARGET-DESIGN-002.md`.
Familles : **T1** (dépassement quantile), **T3** (pics annuels), **T4** (persistance N jours);
**T2** (seuil absolu) en attente HUMain (HDR). Registre multi-définitions **versionné** ;
comparaison **définition par définition**, jamais sur une définition choisie a posteriori.
Fuite : cibles `whole` = **future-informed**, réservées au descriptif ; seules `refhalf`
(**historical/reference**) évaluables (§TARGET-DESIGN-002).

Une cible est un objet journalier binaire `${TARGET_ID}` dérivé d'un run, défini par
(population, quantile, base, min_dur, horizon). Pour la validation, les cibles `-refhalf`:

| cible | définition | horizon |
|---|---|---|
| `T1-q095-refhalf` | primaire : `value > q0.95` calculé sur TRAIN | 1 jour |
| `T1-q099-refhalf` | stress rare : `value > q0.99` calculé sur TRAIN | 1/3/7 jours |
| `T3-peak-q09-refhalf` | pic annuel > q0.9 des pics TRAIN | challenge annuel |
| `T4-q099-N5-refhalf` | run ≥5 j > q0.99 TRAIN | 3/7 jours |

## 7. Fuite / contamination (=== réponse à Q3, formalisée ===)

- **Temporal leakage** : split chronologique §4 avant tout calcul.
- **Filter leakage (target)**: toute variable de calibration est figée sur TRAIN uniquement ;
  jamais de scaling/imputation post-split ; zéro normalisation avant découpage.
- **`threshold_information_time`** : les seuils et quantiles sont classés
  `future-informed` (whole) vs `reference` (refhalf) — seuls `reference` entrent dans
  l'évaluation.
- **Station leakage** : interdit entre GEO-TRAIN et GEO-TEST. Une même station peut traverser
  les partitions du track temporel, puisque celui-ci mesure la généralisation dans le temps.
- **Frontières d'événement** : les runs sont segmentés indépendamment dans VALIDATION, TEST et
  HOLDOUT; aucun événement ne traverse une frontière temporelle.
- Vérification automatique actuelle : `tests/test_m02_reference.py` (seuils futurs, dates,
  régions/stations partagées, frontières de runs et artefacts).

## 8. Baselines (=== réponse à Q5 ===)

Évaluées **dans le même protocole** que le candidat — `benchmark/baselines/README.md` :

| ID | Baseline | Idée | statut |
|---|---|---|---|
| B0 | Climatologie | P(VERY_HIGH_FLOW_EVENT \| mois) — proxy hydrologique empirique | impl |
| B1 | Persistance | Q(t+H) ≈ Q(t) | impl |
| B2 | Saison + persistance | B0 × B1 | impl |
| B3 | Seuil historique | dépasser l'historique de la station | impl |
| B4 | Modèle statistique simple | régression logistique (mois, débit, anomalie) | impl |
| B5 | Modèle ML indépendant | Random Forest / GB (bien spécifiés) | impl |

> PRUDENCE : la saisonnalité est très forte (P(évt) MAM ≈ 0,027 vs 0,002 sep/oct) —
> B0/B2 risquent d'être de très bons compétiteurs ; le candidat doit montrer un **gain
> prédéfini** δ (proposition : +0,05 AUC/PR-AUC) vs B2 ET B5 dans le même protocole, sinon le
> rendement est attribuable au calendrier, pas à la prévision.

## 9. Métriques (=== réponse à Q2/Q4, complétées ===)

Pour toutes cibles, horizons, baselines, et par **saison** + par **symbole (B/E/A)** :

1. AUC-ROC (diagnostic global, jamais seul) ;
2. PR-AUC et precision/recall (évts rares) ;
3. recall au seuil opérationnel + recall top-1 % ;
4. Brier + calibration (reliab) ;
5. courbe performance ↔ horizon journalier : 1, 3 et 7 jours; aucune revendication infrajournalière ;
6. séparation/contamination vérifiée automatiquement (§7).

## 10. Challenge — TRACK-C (prédéfinis)

| ID | Test |
|---|---|
| C1 | Temporal holdout — modèle jamais vu sur TEST |
| C2 | Geographic holdout — stations/régions jamais vues |
| C3 | Extreme-event holdout — évaluation sur événements les plus sévères |
| C4 | Rare-event evaluation — P/R/PR-AUC/recall seuil op. |
| C5 | Horizon journalier — 1, 3 et 7 jours; aucun horizon infrajournalier |
| C6 | Saisonnalité déguisée — A=candidat ; B=mois+jour ; C=saison+débit ; D=candidat sans variables calendaires. Si B≈A, l'AUC est structurale (calendaire), pas prédictive |

Enquête adversarial sans accusation : « le résultat survit-il à des protocoles adversariaux ? ».

## 11. Reproduction — TRACK-R

Reconstruction du candidat champ par champ, sans modification silencieuse :

```text
DATA · FEATURES · TARGET · HORIZON · SPLIT · PREPROCESSING · MODEL · HYPERPARAMETERS · SEED · METRIC
```

Fiches `reproduction/candidate/` — Claim / Independent reproduction / Difference / Possible causes.

## 12. Livrables

01 REPRODUCED · 02 VERIFIED · 03 CHALLENGED · 04 DECISIONAL. « Le code compile », « le résultat
est valide » « a une valeur opérationnelle » sont trois assertions distinctes.

## 13. Registre des expériences

`registry/experiments/{ID}.md` + manifeste : dataset exact + hash · commit · paramètres ·
période · stations · définitions · seed · métriques · artefacts.

## 14. Décisions M02 appliquées, à ré-auditer avant gel

Les décisions D1–D6 et leur portée exacte sont consignées dans `docs/DECISIONS-M02.md`.
Elles sont implémentées mais restent non gelées jusqu'à la ré-audition M03.

## 15. Feuille de route

1. **v0.2 draft — READY_FOR_M03_REAUDIT** (ce document) : D1–D6 appliquées, non gelées.
2. **M03** : ré-audit indépendant des preuves et anomalies restantes.
3. **Gate humain puis v0.2 gel éventuel** : commit daté + hash, sans automaticité.
4. **Baselines B0–B5**, puis réception du prototype comme objet testé.

---

## Annexe A — réponses aux questions Q1–Q5 de la mission

| Q | Réponse (état v0.2-draft) |
|---|---|
| Q1 (matière hydrologique) | Oui : débit journalier national (6 464 stations exploitables, 49,5 M jours valides) + pics annuels (88 556 H) + niveaux non audités en v0.1. |
| Q2 (targets) | T1/T3/T4 définies et quantifiées (target-definitions-v0.1.yaml, DATA-AUDIT-001 §8) ; T2 = HDR. |
| Q3 (fuite) | Seuils whole/refhalf classés (§7) ; détection automatique de leakage au plan. |
| Q4 (splits/métriques) | Splits temporel chrono 70/15/10/5 + géographiques ; métriques §9 (dont stratif saison+symbole). |
| Q5 (baselines) | B0–B5 même protocole ; seuil de gain δ vs B2 et B5 pour le candidat. |
| Phase F (saisonnalité) | P(évt) tables publication (§DATA-AUDIT-001 §9) — pic MAM 0,027 ; alimente B0 et C6. |
| Phase G (splits) | Propositions §4 (temporel + géographique). |
| Phase H | Ce document = la proposition `benchmark/protocols/reference-v0.2-draft.yaml` (statut draft). |
