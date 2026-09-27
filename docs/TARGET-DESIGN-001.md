# TARGET-DESIGN-001 — Conception des cibles (« vérité terrain »)

**Mission : REFERENCE-01 — §9/§10.** Ce document fixe la **définition opérationnelle** des
événements cibles du benchmark (jamais laissée au candidat), la **distinction fuite-vs-pas-fuite**
(§11) et la **comparaison quantitative** mesurée sur la release `20260717` (exploration, pas un
gel). Statut des seuils : **proposition draft** (validation humaine requise, `HUMAN DECISION
REQUIRED` là où indiqué).

---

## 1. Exigences de la mission (rappel)

- Target définie par : **population** (les stations), **observation** (le débit journalier),
  **définition d'événement**, **horizon**, **variable-cible** (binaire), **règle de fuite**
  (`threshold_information_time`) et **échantillonnage** des jours.
- Comparaison des définitions issue de **l'audit DATA-AUDIT-001 §8** — jamais choisie a
  posteriori pour faire « mieux » qu'un candidat.
- Rareté : les événements doivent être **rares mais mesurables** (cf. EVT/PAC, `docs/SOURCES.md`).

## 2. Vocabulaire commun (fixé, non négociable)

```
station_id        numéro HYDAT (8 char)
day               date calendaire
value             débit moyen journalier (m³/s), telle que publique (cellule CRC)
valid             (value > 0) OU (symbole = 'D')      [politique DATA-AUDIT-001 §5]
threshold(s)      quantile de la série de débit (par station)
event             période continue de jours où la condition cible est vraie
run               segment maximal de jours consécutifs vérifiant la condition
target            série binaire jour × station = 1 si le jour est dans un run qualifié
```

Toutes les cibles sont définies **au niveau jour × station** ; l'agrégation par événement
(sommet, durée) est un artefact descriptif produit par l'audit, pas la forme d'évaluation.

## 3. Familles cibles

### T1 — Dépassement de quantile haut (« flow threshold »)

| Paramètre | Valeur testée | Commentaire |
|---|---|---|
| quantile q | 0,95 / 0,99 / 0,995 / 0,999 | haut de distribution = extrémité « crue » |
| base du seuil | série complète (`whole`) vs 1ère moitié (`refhalf`) | cf. §4 fuite |
| condition jour | `value > quantile` | jour strictement au-dessus |
| run | jours consécutifs vérifiant la condition | un événement = un run |
| variable-cible | binaire jour : `1` si jour dans un run | |

Résultats (audit) : voir tableau `DATA-AUDIT-001.md §8`. Ex. q0995-whole : 87 798 événements,
6 237 stations concernées, médiane 2 j, max 135 j, saison MAM 44 619 (50,8 %).

### T2 — Dépassement d'un seuil absolu (« flood threshold ») — **HUMAN DECISION REQUIRED**

HYDAT ne renferme **aucun seuil officiel d'alerte/inondation** (vérifié : vocabulaire
`DATA_SYMBOLS`/`PEAK_CODES` n'en contient pas ; la doc ECCC ne documente pas de seuils
d'avis). Un seuil absolu (ex. palier « crue » par province) **doit être fourni par un humain**
ou repris d'une source règlementaire externe. **Aucun calcul d'événement T2 n'est publié** —
documenté, pas feint. Une cible T2 utilisée dans le benchmark devra déclarer sa provenance
exacte (ordinateur/parution) via `benchmark/protocols/target-definitions-v0.1.yaml`.

### T3 — Pics extrêmes (« peak exceedance »)


| Paramètre | Valeur testée | Commentaire |
|---|---|---|
| source | `ANNUAL_INSTANT_PEAKS`, PEAK_TYPE='H' | pic maximal annuel |
| seuil | quantile q de la distribution des pics maxima ANNUELS (par station) | 0,8 / 0,9 / 0,95 |
| variable-cible | année × station : `1` si pic annuel > quantile | événement = « année à pic exceptionnel » |
| horizon | année hydrologique (ou calendaire, à trancher) | |

Résultats (audit) : q09 : 10 069 événements / 3 357 stations, MAM 4 595 (45,6 %). Il s'agit
d'une cible **annuelle** (rare, ~1/station/50 ans en moyenne) — à distinguer des séries
journalières T1/T4 dans le protocole.

### T4 — Persistance de dépassement (« multi-day exceedance »)


| Paramètre | Valeur testée | Commentaire |
|---|---|---|
| condition jour | `value > quantile q` (même base que T1) | |
| persistance | run de **≥ N** jours consécutifs | N = 3 / 5 / 10 |
| variable-cible | jour : `1` si au moins dans un run de longueur ≥ N | lissage temporel |
| intérêt | événements « durables » (crue soutenue) vs alertes ponctuelles | |

Résultats (audit) : q099-N5 : 28 448 événements, durée médiane 7 j, max 230 j.

## 4. Fuite d'information temporelle (`threshold_information_time`)

Deux métadonnées **obligatoires** sur chaque target (lecture `threshold_information_time`) :

| campagne / suffixe | seuil calculé sur | statut |
|---|---|---|
| `whole-series` (`...-whole`) | **toute** la série (incluant la période d'évaluation) | **future-informed** — pour **diagnostic/descriptif uniquement**, jamais pour évaluer la capacité de prévision |
| `reference`/`refhalf` (`...-refhalf`) | **1ère moitié** du registre de la station uniquement | **historical/reference** — calculable sans fuite, adapté à la comparaison |

Règle : **aucune règle d'évaluation ne peut utiliser une cible marquée `future-informed`.**
L'audit public les deux familles pour documenter la sensibilité, mais le **protocole v0.2 ne
retiendra que la famille `reference`** pour le challenge (§14). Les cibles `whole` servent à
l'analyse descriptive (saisonnalité, rareté) et au calibrage des seuils.

## 5. Décisions de conception prises (mesurées)

1. **Zéros** : la condition `value > quantile` rend les cellules `0.0` non-événements par
   construction — la politique « 0 = ambigu » (`HYDAT-DATA-QUALITY.md` §2) n'affecte pas les
   quantiles hauts ni les événements T1/T3/T4 (impact < 1e-3 sur les seuils). Reste critique
   pour les bas débits (hors périmètre cible v0.2).
2. **Runs pluriannuels** (`refhalf`, jusqu'à 3 663 j) : un seuil figé sur la 1ère moitié peut
   être très bas si cette moitié contient une longue période de faible débit → le run « ne se
   termine jamais ». **Documenté, pas un bug** ; deux options proposées au gel : (a) plafonner
   la durée d'un événement (paramètre `max_event_duration`, valeur proposée 365 j) ; (b)
   exiger un minimum de jours sous seuil entre deux événements (valeur proposée 5 j). **Décision
   hautement recommandée : (a) + (b).** Impact de (a) sur le comptage à estimer avant gel.
3. **Années/saisons** : MAM majoritaire pour toutes les familles (signature nivale) → la cible
   T1/T4 sera évaluée **par saison** (métrique stratifiée, cf. protocole §7 métriques).
4. **Fenêtre froide** : les jours d'hiver (débit sous glace, symbole `B`) restent dans la
   population (politique qualité) mais seront **stratifiés** (B vs non-B) dans le rapport
   d'évaluation — pas d'exclusion.

## 6. Cibles retenues pour le protocole v0.2 (draft — à confirmer au gel)

| ID | Famille | q | base | suffixe | statut info |
|---|---|---|---|---|---|
| `T1-q099-refhalf` | T1 | 0,99 | 1re moitié | reference | historical |
| `T1-q0995-refhalf` | T1 | 0,995 | 1re moitié | reference | historical |
| `T3-peak-q09-refhalf` | T3 | 0,9 (pics) | 1re moitié | reference | historical |
| `T4-q099-N5-refhalf` | T4 | 0,99, N5 | 1re moitié | reference | historical |
| `T2-*` | T2 | ---- | ---- | ---- | **à fournir (HDR)** |

Ces 4 variantes + famille `whole` (diagnostic) constituent le registre v0.1 des cibles :
`benchmark/protocols/target-definitions-v0.1.yaml`.

## 7. Données associées par cible

- `evaluation/reports/DATA-AUDIT-001/target-events.csv` : synthèse (N événements, durées,
  répartitions province/année/saison par target).
- `evaluation/reports/DATA-AUDIT-001/events/{target}.csv` : liste des événements (station,
  start_dte, end_dte, dur, peak_value) — 15 fichiers.
- `benchmark/targets/` : fichiers YAML EXISTANTS proposés dans `target-definitions-v0.1.yaml`
  (ou à générer au gel du protocole).