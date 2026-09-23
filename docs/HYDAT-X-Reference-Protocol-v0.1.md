# HYDAT-X Reference Protocol — v0.1

| Champ | Valeur |
|---|---|
| Version | 0.1 (brouillon à geler) |
| Date | 2026-09-23 |
| Statut | **brouillon** — à geler en v0.2 après arbitrage |
| Projet | 83-HYDAT-X (autonome) |
| Sources amont | `docs/SOURCES.md` ; rapport SCHEMA LIV01 rc3 §9 (T1/T2/T3) ; diagnostic agent-5 |
| Objet | fixer le référentiel expérimental indépendant avant réception du code candidat |

Une fois ce protocole **gelé**, le prototype soumis devient un simple candidat testé contre le
référentiel. Rien dans ce document ne suppose l'accès au code, aux données préparées ni aux
métriques de l'équipe évaluée.

---

## 1. Périmètre

Plateforme de contre-expertise reproductible du prototype d'alerte aux inondations.

Revendication de référence (à tester, jamais admise) :

> 15 ans de données HYDAT, 2 000+ stations, AUC-ROC 0,95 sur données inédites.

Objectifs : **REPRODUCE** (reproduire le résultat annoncé), **CHALLENGE** (robustesse en
conditions indépendantes), **COMPARE** (vs baselines au minimum).

Hors périmètre v0.1 : la chaîne T1 (destinataire, décision, valeur) et le comparateur fédéral
NSRPS/GEM-Hydro sont traités par SCHEMA (rc3 T1 ; R9) — HYDAT-X fournit la matière empirique de
T2/T3 et n'opère aucun jugement politique ou d'autorisation.

## 2. Couches données — gel de la source de vérité

### `data/raw/` — HYDAT_RAW (immuable)

Téléchargements ECCC conservés **intacts**, aucune transformation destructive. Manifeste par
téléchargement (fichier manifeste dans `registry/datasets/`) :

| Champ | Type |
|---|---|
| date | ISO 8601 |
| url / source | source ECCC (archive nationale HYDAT ; temps réel HYDEX/GeoMet) |
| version / fichier | identifiant du produit |
| hash | SHA-256 |
| période couverte | début–fin |
| stations | liste ou plage |
| schéma | format et dictionnaire |
| documentation | doc associée (readme, notice) |

### `data/canonical/` — HYDAT_CANONICAL (normalisé, reproductible)

Format propre, construit par un pipeline versionné, jamais modifié après publication :

```text
station_id, date_time, variable, value, unit, quality_flag, source_file
```

Registre des stations à côté :

```text
station_id, latitude, longitude, drainage_area, province, station_status, record_start, record_end
```

La couche canonical définit ce que nous considérons comme une **observation valide** — pas ce que
le candidat a décidé de traiter.

## 3. Stations admissibles

Critères (seuils chiffrés à décider au gel, valeurs proposées entre parenthèses) :

1. durée d'enregistrement ≥ **X** années (proposition : 10) ;
2. complétude — proportion de jours non manquants ≥ **Y %** (proposition : 80 %) sur la période
   du découpage ;
3. continuité — aucune interruption > **Z** mois (proposition : 12) ;
4. exploitation du `quality_flag` : exclusion systématique des valeurs non validées pour
   l'entraînement ; signalement séparé, jamais silencieux ;
5. sous-échantillons géographiques : provinces, bassins, sous-échantillon « fréquence d'extrêmes »
   — définis pour permettre un C2 géographique.

Résultat : `registry/datasets/stations-v1.parquet` + manifeste.

## 4. Période et découpage

**Séparation temporelle stricte.** Jamais de `train_test_split(random_state=42)`.

```text
TRAIN ──> VALIDATION ──> TEST ──> HOLDOUT      (ordonnancement chronologique, sans interpénétration)
```

- TRAIN : entraînement (proposition : 70 % de la chronique) ;
- VALIDATION : réglage / sélection, toujours postérieure au TRAIN ;
- TEST : évaluation finale du protocole, jamais utilisée pour régler ;
- HOLDOUT : données les plus récentes, réservées à la confrontation finale avec le candidat.

Règle : aucun jour de TEST/HOLDOUT ne peut figurer dans une fenêtre de contexte de TRAIN/VALIDATION.
Aucune normalisation, imputation ni création de variable ne peut être calculée sur l'ensemble
amont avant découpage.

## 5. Définitions d'événement (vérité terrain)

Registre **multi-définitions** — jamais laissé au candidat :

| ID | Définition « inondation » |
|---|---|
| E1 | dépassement d'un percentile haute période (proposition : P95) de la chronique journalière |
| E2 | dépassement d'un seuil historique (débit de crue recensé) |
| E3 | dépassement d'un seuil officiel (avis d'inondation / seuil d'alerte local si disponible) |
| E4 | événement extrême — dépassement du quantile 0,99 ou classement top-N de la série |
| E5 | dépassement simultané de plusieurs niveaux (multivarié / multi-seuil) |

Chaque définition est un objet versionné (`benchmark/targets/`) avec son manifeste. La comparaison
des candidats se fait **définition par définition**, jamais sur une définition choisie a posteriori.
La rareté et les seuils de queue s'appuient sur la littérature EVT/PAC d'agent-1
(`docs/SOURCES.md` §1).

## 6. Baselines de contrôle (obligatoires)

Pistes `models/` — tous évalués dans **exactement le même protocole** que le candidat :

| ID | Baseline | Idée |
|---|---|---|
| B0 | Climatologie | P(inondation \| mois), probabilité empirique |
| B1 | Persistance | Q(t+H) ≈ Q(t) |
| B2 | Saison + persistance | combinaison B0 × B1 |
| B3 | Seuil historique | dépasser l'historique de la station |
| B4 | Modèle statistique simple | régression logistique sur peu de variables (mois, débit, anomalie) |
| B5 | Modèle ML indépendant | Random Forest / XGBoost-LightGBM (bien spécifiés) |

**Règle de lecture** (héritée de rc3 T2) : le candidat doit montrer un **gain prédéfini** — seuil à
décider au gel (proposition : δ = +0,05 AUC/PR-AUC) — par rapport à B2 **et** B5 dans le même
protocole ; à défaut, rendement attribuable au calendrier ou à l'autocorrélation, pas à un
mécanisme de prévision.

## 7. Métriques obligatoires

Publiées pour **toutes** les définitions d'événement, tous les horizons, toutes les baselines :

1. AUC-ROC (diagnostic global, insuffisant seul) ;
2. PR-AUC et precision / recall (événements rares) ;
3. recall au seuil opérationnel (seuil d'alerte), rappel du top-1 % ;
4. Brier score et calibration (fiabilité, rejet histogramme) ;
5. courbe performance ↔ **avance disponible** (lead-time) : 1 h, 3 h, 6 h, 12 h, 24 h, 48 h, 72 h ;
6. séparation temporelle/contamination : vérification automatique, cf. §9.

Artefact minimal publié par expérience : fiche `Claim / Independent reproduction / Difference /
Possible causes` (`reproduction/candidate/`), cf. §9.

## 8. Piste Reproduction — TRACK-R

Spécification reconstruite du candidat, complétée champ par champ, **aucune modification
silencieuse** :

```text
DATA · FEATURES · TARGET · HORIZON · SPLIT · PREPROCESSING · MODEL · HYPERPARAMETERS · SEED · METRIC
```

Produire, pour chaque revendication chiffrée du candidat (AUC 0,95 ; 15 ans ; 2 000 stations ;
données inédites) une fiche de reproduction indépendante : valeur revendiquée, valeur reproduite,
écart, causes possibles.

## 9. Piste Challenge — TRACK-C (prédéfinis)

| ID | Test |
|---|---|
| C1 | Temporal holdout — modèle jamais vu sur la période test |
| C2 | Geographic holdout — stations/régions jamais vues |
| C3 | Extreme-event holdout — évaluation sur les événements les plus sévères uniquement |
| C4 | Rare-event evaluation — precision/recall/PR-AUC/recall au seuil opérationnel |
| C5 | Lead-time sweep — courbe avance disponible (1 h → 72 h) |
| C6 | Saisonnalité déguisée — A = candidat ; B = mois + jour de l'année ; C = saison + débit actuel ; D = candidat sans variables calendaires. Comparer A vs B/C/D : si B ≈ A, l'AUC provient de la structure calendaire, pas d'une capacité prédictive utile |

**Contamination** — vérification automatique appliquée au candidat : fuite temporelle ; variables
calculées avec information future ; interpolation utilisant des observations futures ; mise à
l'échelle avant split ; station présente en train et en test ; duplication de séquences ;
événements voisins à cheval ; target leakage. AUC élevée peut être trompeuse sans mauvaise foi —
le champ d'investigation est « le résultat survit-il à des protocoles adversariaux ? », pas
« l'équipe est-elle fautive ? ».

## 10. Livrables — séparation reproduction / jugement

| Objet | Question |
|---|---|
| `01 — REPRODUCED` | Qu'est-ce que le candidat affirme ? |
| `02 — VERIFIED` | Qu'avons-nous reproduit exactement ? |
| `03 — CHALLENGED` | Que devient le résultat quand on modifie les conditions expérimentales ? |
| `04 — DECISIONAL` | Que signifie la performance pour une décision réelle ? |

Ne jamais confondre « le code fonctionne », « le résultat est valide » et « le résultat a une
valeur opérationnelle ».

## 11. Registre des expériences

Chaque expérience = `registry/experiments/{ID}.md` + manifeste :

```text
dataset (ensemble exact + hash) · commit du code · paramètres · période · stations ·
définition d'événement · seed · métriques · artefacts
```

Le registre transforme le travail en **référentiel de contre-expertise**, pas en deuxième prototype.

## 12. Contribution de Soup

**Outillage périphérique** : Soup (CLI LLM, Apache-2.0, trysoup.dev) intervient dans la couche
évaluation/gating éventuelle (server d'évaluation, logs, gates) **si besoin**. Le référentiel
HYDAT n'est pas construit autour de lui ; le cœur est le pipeline données→événements→splits→
baselines→reproduction→évaluation adversariale.

## 13. Feuille de route

1. **v0.1** (ce document) : arbitrage des seuils et options marquées « proposition » ; statut des
   définitions d'événement E1–E5.
2. **v0.2 — gel** : un seul commit daté + hash, manifestes des datasets et des métriques ;
   constitution de `data/raw/` (téléchargements ECCC, dosettes) et `data/canonical/`.
3. **Baselines premières** : B0–B2 sur le référentiel gelé — avant tout code ML.
4. **Réception du prototype** : le candidat entre comme simple objet testé contre le référentiel.