# Référence — CODEX : plateforme de contre-expertise HYDAT-X

## 0. Identité

| Champ | Valeur |
|---|---|
| Type | proposition d'architecture et de protocole — banc d'essai indépendant de contre-expertise |
| Auteur | Codex (solution externe) |
| Date | 2026-09-23 |
| Contexte de production | mission SCHEMA-LIV01 — réception du diagnostic HYDAT/AUC-ROC/ML et préparation du cycle suivant (prototype à auditer) |
| Objet | construire un référentiel expérimental indépendant pour reproduire, contrôler, challenger et comparer tout modèle de prévision du risque d'inondation soumis à l'équipe |
| Statut | référence archivée — non adoptée telle quelle ; évaluation critique dans `missions/eval-critique-CODEX-HYDAT-X-vs-rc3.md` ; décision ADR-004 ; amorce d'implémentation dans le projet autonome **83-HYDAT-X** (`/home/andrei/Projects/83_HYDAT-X/`) |
| Sources citées | canada.ca HYDAT/HYDEX ; Soup CLI (trysoup.dev) |

Texte reproduit verbatim ci-dessous.

---

Codex dit "Oui. Là, l'objectif est différent : **vous ne voulez pas auditer le prototype qui vous sera remis à partir de son propre environnement ; vous voulez construire votre propre banc d'essai indépendant**, de manière à pouvoir reprendre ses données, ses hypothèses, son protocole et son modèle, puis vérifier vous-même les résultats.

Je structurerais donc le projet comme une **plateforme de contre-expertise reproductible du prototype d'alerte aux inondations**.

ECCC constitue une bonne base indépendante : HYDAT contient les séries hydrométriques archivées de plus de 2 500 stations, tandis que le service temps réel couvre plus de 1 600 stations. ([Canada][1])

## Projet : plateforme de contre-expertise HYDAT

### Mission

> **Construire un référentiel expérimental indépendant permettant de reproduire, contrôler, challenger et comparer tout modèle de prévision du risque d'inondation soumis à l'équipe, sans dépendre du code, des données préparées ou des métriques produites par l'équipe évaluée.**

Le principe est essentiel :

**Prototype soumis**
↓
**Spécification reconstruite**
↓
**Données sources indépendantes**
↓
**Pipeline reproductible**
↓
**Baseline indépendante**
↓
**Reproduction**
↓
**Tests contradictoires**
↓
**Rapport de contre-expertise**

---

# 1. Ce que votre plateforme doit posséder avant de recevoir le prototype

Je créerais cinq couches séparées.

### A. `HYDAT_RAW`

Les données originales téléchargées depuis ECCC, conservées **intactes**.

Aucune transformation destructive.

Pour chaque téléchargement :

* date ;
* URL/source ;
* version/fichier ;
* hash ;
* période couverte ;
* stations ;
* schéma ;
* documentation associée.

HYDAT devient votre **source de vérité**, pas le dataset fourni par l'équipe.

---

### B. `HYDAT_CANONICAL`

Votre propre format normalisé.

Par exemple :

```text
station_id
date_time
variable
value
unit
quality_flag
source_file
```

À côté :

```text
station_id
latitude
longitude
drainage_area
province
station_status
record_start
record_end
```

Cette couche est extrêmement importante.

Elle vous permet de dire :

> « Voici exactement ce que nous considérons comme une observation valide. »

et non :

> « Nous avons utilisé le dataset préparé par le candidat. »

---

# 2. Le référentiel expérimental

Ensuite, vous créez votre **Gold Standard / Reference Benchmark**.

Pas encore de modèle sophistiqué.

Vous définissez précisément :

### Population

Quelles stations ?

Par exemple :

* toutes les stations admissibles ;
* stations ayant ≥ X années ;
* stations ayant suffisamment de données ;
* stations excluant certaines interruptions ;
* éventuellement sous-échantillons géographiques.

### Période

Par exemple :

```text
TRAIN
VALIDATION
TEST
HOLDOUT
```

Mais surtout **séparation temporelle**, pas simplement un `train_test_split(random_state=42)`.

### Événement

C'est probablement la décision méthodologique la plus importante.

Vous devez définir votre propre vérité terrain :

> Qu'est-ce qu'une « inondation » dans le benchmark ?

Possibilités :

* dépassement d'un percentile ;
* dépassement d'un seuil historique ;
* dépassement d'un seuil officiel ;
* événement extrême ;
* dépassement de plusieurs niveaux.

Et vous conservez **plusieurs définitions**, plutôt que de laisser le prototype choisir celle qui lui est favorable.

---

# 3. Le benchmark doit contenir des modèles naïfs

C'est indispensable.

Avant même de reproduire leur IA, votre plateforme doit savoir répondre :

> **« Est-ce que leur modèle fait mieux que quelque chose de très simple ? »**

Je construirais au minimum :

### B0 — Climatologie

```text
P(inondation | mois)
```

### B1 — Persistance

```text
Q(t+H) ≈ Q(t)
```

### B2 — Saison + persistance

### B3 — Seuil historique

### B4 — Modèle statistique simple

Par exemple régression logistique.

### B5 — Modèle ML indépendant

Par exemple :

* Random Forest ;
* XGBoost/LightGBM ;
* éventuellement réseau neuronal.

Ce sont vos **baselines de contrôle**.

Ainsi, si le candidat annonce :

> AUC = 0,95

vous pouvez répondre :

> « Notre baseline saison + persistance obtient 0,91 dans exactement le même protocole. »

La question devient alors beaucoup plus intéressante.

---

# 4. Puis arrive le « Reproduction Track »

Je créerais une piste séparée :

## `TRACK-R — Reproduction`

Objectif :

> **reproduire exactement le résultat annoncé par l'équipe.**

On documente :

```text
DATA
FEATURES
TARGET
HORIZON
SPLIT
PREPROCESSING
MODEL
HYPERPARAMETERS
SEED
METRIC
```

Et surtout :

### aucune modification silencieuse.

Si le prototype dit :

> 15 ans de données
> 2 000 stations
> AUC 0,95

votre plateforme doit pouvoir produire une fiche :

```text
Claim:
AUC = 0.95

Independent reproduction:
AUC = 0.XX

Difference:
-0.XX

Possible causes:
[ ]
```

---

# 5. Puis le « Challenge Track »

C'est là que votre **contre-expertise** devient vraiment intéressante.

Vous ne cherchez plus seulement à reproduire leur expérience.

Vous cherchez à savoir **où elle cesse de fonctionner**.

Je créerais des tests prédéfinis.

### C1 — Temporal holdout

Le modèle n'a jamais vu la période test.

### C2 — Geographic holdout

Le modèle n'a jamais vu certaines stations/régions.

### C3 — Extreme-event holdout

Évaluation exclusivement sur les événements les plus sévères.

### C4 — Rare-event evaluation

Precision/Recall, PR-AUC, recall à seuil opérationnel, etc.

### C5 — Lead-time sweep

Au lieu d'un seul chiffre :

```text
1 h
3 h
6 h
12 h
24 h
48 h
72 h
```

Vous obtenez alors une courbe :

**performance ↔ avance disponible.**

Et c'est probablement beaucoup plus informatif que l'AUC unique.

---

# 6. Test particulièrement important : « saisonnalité déguisée »

Je ferais de celui-ci un test officiel.

Construire :

```text
Model A = modèle proposé
Model B = mois + jour de l'année
Model C = saison + débit actuel
Model D = modèle proposé sans variables calendaires
```

Puis comparer.

Si :

```text
AUC modèle = 0.95
AUC saisonnalité = 0.92
```

le résultat doit être interprété très différemment de :

```text
AUC modèle = 0.95
AUC saisonnalité = 0.61
```

Vous testez ainsi directement l'affirmation :

> « le modèle a identifié de façon autonome les tendances saisonnières »

sans confondre **détection de structure** et **capacité prédictive utile**.

---

# 7. Une deuxième couche : la contamination

Votre plateforme doit également rechercher automatiquement :

* fuite temporelle ;
* variables calculées avec information future ;
* interpolation utilisant des observations futures ;
* normalisation réalisée avant le split ;
* station présente simultanément dans train et test ;
* duplication de séquences ;
* événements voisins présents dans train et test ;
* target leakage.

C'est un domaine où une AUC extrêmement élevée peut devenir trompeuse sans qu'il y ait nécessairement mauvaise foi.

Le principe de votre contre-expertise doit donc être :

> **nous ne cherchons pas une erreur ; nous cherchons à déterminer si le résultat survit à des protocoles de plus en plus adversariaux.**

---

# 8. Je séparerais complètement « reproduction » et « jugement »

Votre architecture devrait produire quatre objets.

### `01 — REPRODUCED`

> Qu'est-ce que le candidat affirme ?

### `02 — VERIFIED`

> Qu'avons-nous pu reproduire exactement ?

### `03 — CHALLENGED`

> Que se passe-t-il lorsque nous modifions les conditions expérimentales pertinentes ?

### `04 — DECISIONAL`

> Que signifie finalement la performance pour une décision réelle ?

Cela évite de mélanger :

**« le code fonctionne »**

avec :

**« le résultat est valide »**

et avec :

**« le résultat a une valeur opérationnelle ».**

---

# 9. Et Soup ?

Je le traiterais comme **un outil périphérique**, pas comme le cœur de votre infrastructure.

La philosophie de Soup est intéressante pour votre projet parce qu'il formalise notamment les évaluations, les baselines, les gates et les artefacts reproductibles ; sa documentation insiste également sur le fait qu'un résultat amélioré sur une tâche ne suffit pas à justifier un passage en production. ([Soup CLI][2])

Mais votre problème n'est pas principalement du LLM.

Votre cœur technique devrait plutôt être :

```text
HYDAT
  ↓
Data lake immuable
  ↓
Canonical dataset
  ↓
Event definition
  ↓
Temporal splits
  ↓
Benchmark registry
  ↓
Baselines
  ↓
Candidate reproduction
  ↓
Adversarial evaluation
  ↓
Evidence registry
  ↓
Counter-expertise report
```

Soup peut éventuellement intervenir **dans la couche d'évaluation/gating**, mais je ne construirais pas le référentiel HYDAT autour de lui.

---

# 10. Le livrable que je vous propose de construire

Je donnerais au projet un nom distinct de DELTA-5 :

## **HYDAT-X — Independent Flood Prediction Benchmark**

avec trois objectifs :

**REPRODUCE**
Reproduire le résultat annoncé.

**CHALLENGE**
Tester sa robustesse dans des conditions indépendantes.

**COMPARE**
Comparer au minimum aux baselines et aux alternatives.

Et surtout, votre plateforme doit être prête **avant de voir le code du candidat**.

C'est ce qui donne sa valeur à la contre-expertise.

---

## Architecture initiale

Je partirais sur quelque chose de relativement simple :

```text
hydat-x/
│
├── data/
│   ├── raw/
│   ├── canonical/
│   └── reference/
│
├── metadata/
│   ├── stations/
│   ├── downloads/
│   └── provenance/
│
├── benchmark/
│   ├── targets/
│   ├── splits/
│   ├── baselines/
│   └── protocols/
│
├── models/
│   ├── persistence/
│   ├── seasonal/
│   ├── statistical/
│   └── ml/
│
├── reproduction/
│   └── candidate/
│
├── challenge/
│   ├── temporal/
│   ├── geographic/
│   ├── extreme/
│   ├── leakage/
│   └── lead_time/
│
├── evaluation/
│   ├── metrics/
│   ├── calibration/
│   └── reports/
│
└── registry/
    ├── datasets/
    ├── experiments/
    └── evidence/
```

Et **chaque expérience reçoit un identifiant et un manifeste** : dataset exact, commit du code, paramètres, période, stations, définition de l'événement, seed, métriques et artefacts.

C'est cela qui transformera votre travail en **référentiel de contre-expertise**, plutôt qu'en deuxième prototype.

### Première phase que je vous recommande

Ne commençons **pas** par coder le modèle ML.

Commençons par construire le **« HYDAT-X Reference Protocol v0.1 »** : précisément quelles données HYDAT nous gelons, quelles stations nous retenons, comment nous définissons les événements, comment nous faisons les splits temporels, quelles baselines nous imposons et quelles métriques deviennent obligatoires.

Une fois ce protocole gelé, **le prototype qui vous sera soumis devient simplement un candidat à tester contre votre référentiel**.

[1]: https://www.canada.ca/fr/environnement-changement-climatique/services/eau-apercu/volume/surveillance/releves/produits-donnees-services.html?utm_source=chatgpt.com "Produits de données des relevés hydrologiques et services - Canada.ca"
[2]: https://trysoup.dev/?utm_source=chatgpt.com "Soup CLI: build, expect, train, x-ray, merge, bisect, ship, one CLI"