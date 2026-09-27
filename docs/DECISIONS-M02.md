# Décisions M02 — reconstruction de la référence

Statut : **appliquées, non gelées**, en attente de ré-audit M03.

| Décision | Application M02 |
|---|---|
| D1 | `VERY_HIGH_FLOW_EVENT` est un proxy de débit très élevé, jamais une vérité terrain d'inondation. |
| D2 | Cible primaire `T1-q095-refhalf`; seuil Q95 par station calculé exclusivement sur TRAIN (`≤ 2010-12-31`), puis appliqué en 2011–2025. |
| D3 | `T1-q099-refhalf` = stress rare; `T3-peak-q09-refhalf` = challenge extrême; `T4-q099-N5-refhalf` = challenge de persistance. |
| D4 | Une lacune calendaire `> 1 jour` coupe un run et `span == dur`; aucun minimum pour T1, N5 reste une cible distincte. |
| D5 | Données journalières : horizon primaire 1 jour; challenges 3 et 7 jours. Aucune revendication 1 h/3 h/6 h/12 h. |
| D6 | Deux objets séparés : TRACK-TEMPORAL par dates strictes et runs bornés à chaque partition; TRACK-GEOGRAPHIC à stations et régions train/test disjointes. |

Le suffixe historique `refhalf` désigne désormais l'information de référence autorisée,
explicitement matérialisée par TRAIN. Il ne signifie plus « moitié calculée sur la chronique
complète », mécanisme qui dépendait implicitement du futur.
