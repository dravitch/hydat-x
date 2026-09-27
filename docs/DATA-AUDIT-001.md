# DATA-AUDIT-001 — Audit des données HYDAT (release 20260717)

**Mission : REFERENCE-01 — livrable « audit des données » (§5).** Lecture seule, base brute
jamais modifiée (`ATTACH … READ_ONLY`), SHA-256 vérifiée. Chiffres brut traçables au script et
aux CSV de `evaluation/reports/DATA-AUDIT-001/`.

---

## 1. Sources et périmètre

| Champ | Valeur |
|---|---|
| Base | `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` |
| SHA-256 | `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517` (vérifié vs `MANIFEST.sha256`) |
| Release ECCC | `20260717` (période déclarée 1850–2026) |
| Schéma SQLite | 33 tables, 3 719 056 lignes (`tables.csv`) |
| Outillage | `scripts/audit_hydat.py` (lecture seule, DuckDB sur SQLite + parquet `logs/audit/dly_flows.parquet`) |
| Reproducibilité | `nix develop && python scripts/audit_hydat.py` (≈ 285 s) — parquet mis en cache |

## 2. Schéma relationnel (relations principales identifiées)

```text
STATIONS (1) ──< STATION_NUMBER, HISTORY >=─< STATION_NAME, HISTORY_DETAILS
     │
     ├─< STN_DATA_RANGE      (registre début/fin, par STATION_NUMBER + DATA_TYPE)
     ├─< DLY_FLOWS           (débit moyen journalier, lignes nouveaux-format mois/station)
     │     ├─ FLOW1..31 · FLOW_SYMBOL1..31 · FLOW_SYMBOL_CD?  → DATA_SYMBOLS (SYMBOL)
     │     ├─ FULL_MONTH (0/1) · NO_DAYS (nb jours du mois) → % jours calendaires du mois
     │     └─ MONTHLY_TOTAL (somme mensuelle — utilisé pour la cohérence, non publié en v0.1)
     ├─< DLY_LEVELS          (niveaux d'eau — non audités dans cet audit v0.1)
     ├─< ANNUAL_STATISTICS   (AS_Statistic … par année)
     ├─< ANNUAL_INSTANT_PEAKS (pic annuel, PEAK_TYPE→PEAK_CODES H/L, PRECISION_CODE→PRECISION_CODES)
     └─< DLY_HEIGHT??        (non présent — vérifié par inventaire)
Référentiels (dimensions) : DATA_TYPES (H/Q/I/S/T), DATA_SYMBOLS (A/B/D/E/S),
PEAK_CODES (H/L), PRECISION_CODES (8/9), AGENCY_LIST (252 agents), OPERATION_CODES.
```

**Écart de vocabulaire constaté** : le code officiel `DATA_SYMBOLS` contient exactement
A/B/D/E/S. En données réelles on observe en plus le symbole espace `' '` (1 161 cellules),
hors vocabulaire officiel → signalé, non interprété (cf. `HYDAT-DATA-QUALITY.md` §3.4).

## 3. Inventaire

- **33 tables**, 3 719 056 lignes totales (détail colonnes/types/clés candidates : `tables.csv`).
- Table la plus volumineuse : `DLY_FLOWS` (1 779 871 lignes mois/station, ~53,0 M de cellules
  jour), puis `ANNUAL_STATISTICS` (201 916), `ANNUAL_INSTANT_PEAKS` (182 723), `DLY_LEVELS`.
- **Q1 (§5)** — `Powder` oui : la base contient l'historique journalier national sous forme de
  cellules jour par ligne et les pics annuels.

## 4. Stations

- **8 057 stations** ; **2 896 actives** ; coordonnées : 8 057 (100 %) ; superficie de drainage
  déclarée : 7 713 (96 %) ; réseau RHBN « recherche » : 314.
- Durée d'enregistrement (depuis STN_DATA_RANGE, tous types) : `>30 ans` 2 291, `10-30 ans`
  1 853, `<10 ans` 2 334, `NA` 1 579.
- Répartition provinciale dominante : BC 2 324, ON 1 119, AB 1 104, QC 1 001, SK 748, MB 659.

## 5. Couverture temporelle (débit journalier)

- Stations avec **≥1 jour de débit valide** : **6 464**.
- **14 stations éliminées** : cellules présentes mais **0 observation valide** (tous jours 0.0
  ou symboles non-D) — `05HA037 05HA045 05HA068 08DA007 08HA007 08LB059 08NM201 11AB042
  11AB051 11AB052 11AB053 11AC036 11AC042 11AC046`.
- Jours valides totaux : **49 548 861** ; médiane par station **4 112** jours.
- Jours `0.0` sans symbole (ambigu) : **2 681 900** — politique : jamais supposés
  (`HYDAT-DATA-QUALITY.md` §2, `HUMAN DECISION REQUIRED`).
- **Couverture médiane** (jours valides / registre STN_DATA_RANGE) : **0,7991** ; médiane jours
  manquants : 604. Détail : `coverage.csv` (par station), `temporal-coverage.parquet`
  (station × année), `missingness.csv` (par station sur les lignes mois).

## 6. Qualité & missingness

| Indicateur | Valeur |
|---|---|
| Symboles jours : vide/NULL, B(glace), E(estimé), A(partiel), `' '`(espace) | 39 696 508 / 10 157 834 / 2 788 490 / 376 961 / 1 161 |
| Jours `0.0` sans symbole (ambigu) | 2 681 900 |
| `0.0` avec symbole B / E / A | 642 659 / 132 049 / 14 003 |
| `FULL_MONTH=1` (mois complet) | 1 720 863 (97 %) |
| PRECISION_CODE pics : NULL / 8 / 9 | 110 785 / 68 468 / 3 470 |

Interprétations et politiques détaillées : `docs/HYDAT-DATA-QUALITY.md`. Aucun flag supposé ;
les trois HUMAN DECISION REQUIRED sont listés dans la section *Décisions ouvertes*.

## 7. Pics annuels (phase extrêmes)

- Pics **H** (max) : **88 556** ; pics **L** (min) : 22 229 ; **3 546 stations** concernées ;
  période 1904–2025.
- Pics H par année : min 1, **médiane 515**, max 1 809.
- Relation pics vs série journalière : comparaison partielle faite dans le script (phase
  `extremes`) — le max annuel de `ANNUAL_INSTANT_PEAKS` est cohérent en ordre de grandeur avec
  le max journalier de `DLY_FLOWS` sur les stations/périodes communes ; écart possible sur les
  stations à faible résolution. (Phase complète de consolidation à isoler dans un audit dédié si
  la cible T3 l'exige.)

## 8. Targets — résultats quantitatifs (comparaison T1/T3/T4)

| Target | N événements | stations w/≥1 év | durée méd | durée max |
|---|---|---|---|---|
| T1-q095-whole | 447 134 | 6 402 | 3 | 470 |
| T1-q099-whole | 148 200 | 6 309 | 2 | 230 |
| T1-q0995-whole | 87 798 | 6 237 | 2 | 135 |
| T1-q0999-whole | 25 873 | 6 071 | 1 | 40 |
| T1-q095-refhalf | 238 799 | 5 840 | 3 | **3 663** |
| T1-q099-refhalf | 85 076 | 5 336 | 2 | 3 663 |
| T3-peak-q08-whole | 18 249 | 3 360 | 1 | 1 |
| T3-peak-q09-whole | 10 069 | 3 357 | 1 | 1 |
| T3-peak-q095-whole | 6 006 | 3 351 | 1 | 1 |
| T4-q095-N3 / N5 | 223 909 / 140 802 | 6 225 / 6 000 | 6 / 9 | 470 / 470 |
| T4-q099-N3 / N5 / N10 | 54 554 / 28 448 / 8 937 | 5 475 / 4 534 / 2 699 | 5 / 7 / 14 | 230 / 230 / 230 |

- T1/T4 : détection par **segmentation en runs** jour > seuil ; durée d'un événement = longueur
  du run ; gaps et fins de séries coupent les runs. T3 : événement = pic seul (dur 1).
- Seuils par station : quantiles de la série (période entière = `whole`, future-informed,
  marqués §11 leakage) ou 1ère moitié du registre (`refhalf`, historical/reference). Années
  dominantes (1974, 2011, 2020) et saison MAM cohérentes avec la crue nivale (phase F).
- Anomalie notable : `refhalf` produit des runs **pluriannuels** (jusqu'à 3 663 j) pour des
  stations à faible signal — dû au seuil figé sur la 1ère moitié conservateur vs 2e moitié
  d'observation ; **documentation requise** dans TARGET-DESIGN-001.md (attendu, pas un bug).

## 9. Saisonnalité (phase F)

`P(jour en excès q099 | jour) par mois` (T1-q099-whole) :

```
m1:0.004  m2:0.004  m3:0.008  m4:0.023  m5:0.027  m6:0.023
m7:0.009  m8:0.003  m9:0.002  m10:0.003 m11:0.004 m12:0.004
```

- **Pic de crue en mai (0,027)** suivi d'avril (0,023) et juin (0,023) ; minimum en
  septembre-octobre (0,002) — signature de la **fonte des neiges / régime nival** dominant au
  Canada. Cohérent avec la saison MAM dominante des événements T1/T3/T4.
- Base description (pas de ML) : la seasonality feed B0 (climatologie) et le challenge C6
  (saumon calendaire déguisé).

## 10. Décisions ouvertes (HUMAN DECISION REQUIRED) — résumé

| # | Décision | Enjeu chiffré | Lieu |
|---|---|---|---|
| D1 | 0.0 sans symbole = manquant ou zéro réel ? | 2,68 M jours (5,1 %) | `HYDAT-DATA-QUALITY.md` §2 |
| D2 | exclure 14 stations sans jour valide ? | 14 stations | `HYDAT-DATA-QUALITY.md` §4 |
| D3 | T2 (seuil absolu) : seuil officiel ? | Aucun dans HYDAT | `TARGET-DESIGN-001.md` |
| D4 | runs pluriannuels refhalf : tolérables ? | 21 runs >1 an | `TARGET-DESIGN-001.md` §5 |

## 11. Traçabilité

Requêtes SQL intégrées dans `scripts/audit_hydat.py` (une par section, commentées) ; artefacts :
`evaluation/reports/DATA-AUDIT-001/{tables.csv, stations.csv, coverage.csv, missingness.csv,
distributions.csv, annual-peaks.csv, target-events.csv, seasonality.csv,
temporal-coverage.parquet, events/*.csv (15), summary.json, report.md}`.

Sourcées ECCC : `data/raw/hydat/20260717/documentation/HYDAT_Definition_*.pdf` (importées en
`/tmp/opencode/hydat_def_{en,fr}.txt`), `HYDAT_ReleaseNotes_20260717_*.pdf`, `registry/datasets/
hydat-reference-20260717.yaml`.