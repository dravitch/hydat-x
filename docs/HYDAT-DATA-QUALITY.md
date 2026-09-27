# HYDAT-DATA-QUALITY.md — Interprétation de la qualité & missingness HYDAT

**Mission : REFERENCE-01 (données réelles, release `20260717`).**

Ce document décrit l'interprétation des champs de qualité HYDAT **telle que documentée par
l'ECCC** et les décisions d'exploitation appliquées dans l'audit `DATA-AUDIT-001`. Règle
d'or de la mission : **ne jamais inventer la sémantique d'un flag** (§7) ; toute interprétation
incertaine est marquée `HUMAN DECISION REQUIRED`.

---

## 1. Champs de qualité identifiés dans HYDAT

| Table | Champ | Type | Source doc |
|---|---|---|---|
| `DATA_SYMBOLS` | `SYMBOL` | vocabulaire | `HYDAT_Definition_EN.pdf` (Data symbols) |
| `FLOW_SYMBOL1..31` | symbole journalier du débit | par jour | `DLY_FLOWS` |
| `LEVEL_SYMBOL1..31` | symbole journalier du niveau | par jour | `DLY_LEVELS` |
| `PEAK_CODES` | code H/L (max/min) | vocabulaire | `HYDAT_Definition_EN.pdf` |
| `PRECISION_CODES` | précision de saisie | vocabulaire | `HYDAT_Definition_EN.pdf` |
| `ANNUAL_INSTANT_PEAKS.PRECISION_CODE` | précision d'un pic | occurrence | `ANNUAL_INSTANT_PEAKS` |
| `DLY_FLOWS.FULL_MONTH` | mois complet ? (0/1) | par mois | `HYDAT_Definition_EN.pdf` |
| `DLY_FLOWS.NO_DAYS` | nb de jours du mois | par mois | `HYDAT_Definition_EN.pdf` |
| `STN_DATA_RANGE` | registre début/fin par station | par station | table HYDAT |

Valeur mesurée du vocabulaire `DATA_SYMBOLS` (extrait vérifié de la base) :

| Symbole | Signification doc ECCC | Utilisation dans l'audit |
|---|---|---|
| `A` | Partial Day (jour partiel de données) | observation valide |
| `B` | Ice Conditions (conditions de glace) | observation valide (débit réel, souvent réduit par glace) |
| `D` | Dry (jour sec — **vrai zéro mesuré**) | observation valide, valeur 0 |
| `E` | Estimated | observation valide, **comptée** (marquée `n_est`) |
| `S` | Sample(s) collected this day | non pertinente pour le débit, non observée dans DLY_FLOWS |

`OPERATION_CODES` : C=Continuous, M=Miscellaneous, S=Seasonal (non utilisés pour l'audit
journalier). `PRECISION_CODES` : `8` = mètres au millimètre, `9` = centimètres (doc
`HYDAT_Definition_EN.pdf`).

---

## 2. Le cas « 0.0 sans symbole » — AMBIGU, `HUMAN DECISION REQUIRED`

La doc HYDAT ne définit **pas explicitement** la cellule `0.0` avec symbole vide (`''`/NULL)
dans `DLY_FLOWS.FLOWn`.

Constats mesurés (audit, release `20260717`) :

| Catégorie | nb jours |
|---|---|
| cellules non nulles au total (53,0 M jours de mois) | 53 020 954 |
| **`0.0` sans symbole** | **2 681 900** (5,06 %) |
| `0.0` avec symbole `B` (glace) | 642 659 |
| `0.0` avec symbole `E` (estimé) | 132 049 |
| `0.0` avec symbole `A` (partiel) | 14 003 |
| `0.0` avec symbole `' '` (espace, hors vocabulaire officiel A/B/D/E/S) | 0 |
| valeurs non nulles avec symbole `' '` (espace) | 1 161 |
| jours valides (valeur>0 **ou** symbole `D`) | 49 548 861 |

### Pourquoi ce n'est pas tranché objectivement

- `MONTHLY_TOTAL` = somme des cellules du mois : un `0.0` silencieux contribue 0 à la somme,
  **identique** dans les deux hypothèses (zéro réel vs manquant) → impossible de discriminer
  par la cohérence mensuelle.
- L'ECCC documente le **symbole `D` pour les vrais jours secs** : un `0.0` sans `D` n'est donc
  *a priori* pas un jour sec mesuré, mais la doc n'affirme jamais qu'il s'agit d'une donnée
  manquante.
- **Constats mesurés supplémentaires de l'audit** :
  - le symbole `D` (`Dry`) a **0 occurrence** dans `DLY_FLOWS` (toute la base) — l'ECCC semble
    encoder les jours secs comme `0.0` **sans symbole** et/ou avec `B` (glace) ;
  - il n'existe **aucune cellule à 0.0 avec une valeur de symbole espace** (0 cellule) ;
  - les symboles espace `' '` (1 161 cellules) portent tous des **valeurs non nulles**.
- La convention utilisée dans la pratique par de nombreux consommateurs HYDAT traite ces
  cellules comme des données manquantes, mais **ce n'est pas une vérité documentée ECCC**.

### Décision d'exploitation appliquée dans l'audit (par défaut conservatrice)

```text
jour valide  ⇔  (valeur > 0)  OU  (symbole = 'D')
tout 0.0 sans symbole  → non-observation (compté n_zero_blank, jamais supposé)
```

Conséquence mesurée sur la population : **2,68 M de jours** (5,1 % des cellules de mois) sont
exclus des « jours valides ». L'impact sur les quantiles hauts (Q95+ utilisés pour les targets)
est **négligeable par construction** : les zéros ne dépassent jamais un seuil haut. L'impact réel
concerne l'estimation des bas débits et des comptages de jours.

> **`HUMAN DECISION REQUIRED`** : trancher, pour le protocole gelé, si ces cellules sont des
> manquants (politique actuelle P-valide) ou des zéros réels. L'audit publie les deux comptages
> pour permettre la décision (risque chiffré : 5,1 % des jours).

---

## 3. Autres constats qualité mesurés

### 3.1 Symboles de débit (jours de mois, toutes cellules)

| symbole | nb jours |
|---|---|
| vide/NULL | 39 696 508 |
| `B` (glace) | 10 157 834 |
| `E` (estimé) | 2 788 490 |
| `A` (partiel) | 376 961 |
| `' '` (espace) | 1 161 |

- **`B` (glace) = 10,2 M de jours** : très courant ; le débit reste exploitable mais correspond
  souvent à une mesure perturbée par la glace — à signaler dans le protocole (règle qualité
  `quality_rules`), la valeur n'étant *pas* invalidée par la doc.
- **`E` (estimé) = 2,9 M de jours** : observé mais estimé ; l'audit les **inclut** dans les
  quantiles (n_est compté à part), respects de la politique « signaler séparément, jamais
  supprimer silencieusement ».

### 3.2 FULL_MONTH (DLY_FLOWS)

| FULL_MONTH | nb mois |
|---|---|
| 1 (complet) | 1 720 863 |
| 0 (incomplet) | 59 008 |

90 %+ des mois sont complets (1 720 863 / 1 779 871 mois). Les 59 008 mois incomplets confirment
qu'une fraction des mois comporte des trous → compter `NO_DAYS` (< jours calendaires) pour la
définition de « mois exploitable ».

### 3.3 PRECISION_CODE des pics annuels

| PRECISION_CODE | nb pics |
|---|---|
| NULL | 110 785 |
| 8 (mm) | 68 468 |
| 9 (cm) | 3 470 |

60 % des pics n'ont **aucune précision renseignée** ; le reste en millimètres (30 %) ou
centimètres (5 %). Aucun pic n'est donc assorti d'une incertitude exploitable — le protocole ne
doit pas prétendre connaître la précision d'un pic non renseigné.

### 3.4 Anomalies identifiées (à surveiller)

1. `DATA_SYMBOLS` contient exactement 5 valeurs (A/B/D/E/S) ; en base, on observe en plus
   `' '` (espace) sur 1 161 cellules, toutes de valeur non nulle (0 jour à 0.0). **Hors
   vocabulaire officiel** — signalé, non interprété (HUMAN DECISION REQUIRED pour l'exclusion).
2. Stations présentant des **cellules mais 0 observation valide** (tous jours 0.0/symboles
   non-D) — cf. §4 ci-dessous.
3. Périodes de fins d'enregistrements avec `RHBN` (réseau de référence hydrologique) :
   314 stations RHBN (statut réseau de recherche, valeurs réputées de meilleure qualité —
   signaler, ne pas supposer).

---

## 4. Stations à cellule mais sans débit valide — à exclure

L'audit (`coverage.csv`) identifie **14 stations** avec des cellules de flux mais **zéro jour
valide** (tous jours `0.0`/symboles non-D) :

```
05HA037 05HA045 05HA068 08DA007 08HA007 08LB059 08NM201
11AB042 11AB051 11AB052 11AB053 11AC036 11AC042 11AC046
```

Contre-vérification d'enregistrement (`STN_DATA_RANGE` DATA_TYPE='Q') : certaines ont un
registre déclaré (ex. 11AC036 1912–1912, 08NM201 1973–1973) mais un contenu journalier sans
aucun débit positif. Ces stations encrassent la population exploitable du benchmark → proposées
à l'exclusion dans `benchmark/protocols/reference-v0.2-draft.yaml` (règle : ≥1 jour valide).

---

## 5. Politiques de qualité retenues pour le protocole v0.2 (draft)

| Règle | Valeur proposée | Justification mesurée |
|---|---|---|
| jour valide | `value>0` OU `symbol='D'` | §2 (0.0 silencieux = ambigu) |
| jours `E` (estimés) | inclus, comptés `n_est` | doc : « larger than expected error », pas invalidé |
| jours `B` (glace) | valides, signalés | 10,2 M jours — exclusion massive sinon |
| mois exploitable | `FULL_MONTH=1` OU `NO_DAYS` = jours calendaires | 3,4 % des mois incomplets |
| stations exploitables | ≥1 jour valide | 14 stations éliminées par cette règle |
| pics | `PEAK_CODE='H'` uniquement pour le max | `PEAK_CODES` H=Maximum |
| précision | jamais supposée | §3.3 (60 % NULL) |

Statut : **draft** — toutes les valeurs ci-dessus sont des propositions à valider par un humain
(C6 mission : « Oui je valide / Non voici ce qui doit être modifié »).

---

## 6. Traçabilité

Chaque ligne de §2–§4 provient de `scripts/audit_hydat.py` (phase `quality`, `coverage`) exécuté
sur `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` (sha256 vérifiée `9185ea30…ef517`).
Résultats bruts : `evaluation/reports/DATA-AUDIT-001/missingness.csv`, `coverage.csv`,
`summary.json`.