# Target design 002

Statut : **reference-not-frozen**. Toutes les cibles sont des proxies hydrologiques et non des
observations d'inondation ou de dommage.

| Cible | Rôle | Seuil TRAIN | Événements | Stations | Médiane / max |
|---|---|---:|---:|---:|---:|
| T1-q095-refhalf | PRIMARY | Q95 journalier/station | 92 634 | 2 092 | 2 / 678 j |
| T1-q099-refhalf | RARE-STRESS | Q99 journalier/station | 32 819 | 2 044 | 2 / 663 j |
| T3-peak-q09-refhalf | EXTREME-CHALLENGE | Q90 des pics H/station | 3 442 | 1 342 | 1 / 1 j |
| T4-q099-N5-refhalf | PERSISTENCE-CHALLENGE | Q99 journalier/station | 6 708 | 1 618 | 8 / 663 j |

Référence : toutes les observations autorisées jusqu'au 2010-12-31. Application : 2011-01-01
à 2025-12-31. Le seuil est strict (`value > q`). Une lacune supérieure à un jour interrompt
un run. T1 n'impose aucune durée minimale; T4 impose cinq jours. Les 0 violations de
`span == dur` sont contrôlées par test.

Les runs sont segmentés indépendamment dans VALIDATION, TEST et HOLDOUT : aucun événement ne
peut utiliser des jours d'une partition future. Une frontière de split coupe donc un run aux
fins de l'évaluation, même lorsque le phénomène hydrologique est continu.

Horizon primaire : 1 jour. Horizons de challenge : 3 et 7 jours. Les données quotidiennes ne
permettent aucune conclusion aux horizons 1 h, 3 h, 6 h ou 12 h.

Définitions machine : `benchmark/targets/*.yaml`; événements et seuils :
`evaluation/reports/DATA-AUDIT-002/{events,targets}/`.
