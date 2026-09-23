# HYDAT-SOURCE — la base nationale canadienne

## Qu'est-ce que HYDAT ?

**HYDAT** est l'archive nationale des données hydrométriques du Canada, maintenue par
**Environnement et Changement climatique Canada (ECCC)** : débits, niveaux et sédiments mesurés
sur le réseau de stations hydrométriques national. C'est la source de vérité hydrométrique pour le
référentiel HYDAT-X.

Diffusion officielle : `https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/`
(index public ; une archive `Hydat_sqlite3_<AAAAJJMM>.zip` par mise à jour, avec un format
`Hydat_mdb_<AAAAJJMM>.zip` équivalent en Access/MDB).

## HYDEX vs HYDAT — ne pas confondre

| | **HYDAT** | **HYDEX** |
|--|-----------|-----------|
| Nature | **Archive historique complète** (débits/niveaux/sédiments, séries longues, référentiel de stations) | Service de consultation/exposition (API/web) autour du même patrimoine hydro |
| Utilisé ici | **Oui — le corps du référentiel** (release complète, gelée, avec PDFs de définition et notes de version) | **Non retenu comme source** : expose un sous-ensemble selon l'API/moment de consultation, inadapté à un gel reproductible |

Le protocole HYDAT-X fonde ses artefacts d'évaluation sur l'archive **HYDAT** (stable, datée,
hashée), et non sur HYDEX.

## Version référencée

- **Release** : `20260717`
- **Mise à disposition** (index ECCC) : supposée ≤ 2026-07-17 ; **récupération réelle** :
  `2026-09-23T08:48Z` (UTC)
- **Format retenu** : `Hydat_sqlite3_20260717.zip` (SQLite ; le compagnon MDB n'est pas
  téléchargé car le format SQLite est préféré — moteur auditable, requêtable, versionnable)
- **Documentation archivée aux côtés de la base** :
  - `HYDAT_Definition_EN.pdf` / `HYDAT_Definition_FR.pdf` (dictionnaire des tables/colonnes)
  - `HYDAT_ReleaseNotes_20260717_EN.pdf` / `HYDAT_ReleaseNotes_20260717_FR.pdf`

## Contenu constaté (inspection lecture seule, 2026-09-23)

- **Base** : `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` (1 296 893 952 octets) ; ouverte en
  `mode=ro` uniquement.
- **33 tables** (+ aucune table système significative), **8 057 stations** dans `STATIONS`.
- **Période de couverture** (bornes `STN_DATA_RANGE`) : **1850 → 2026**.
- Familles de tables :
  - Référentiel stations : `STATIONS`, `STN_DATA_COLLECTION`, `STN_DATA_RANGE`,
    `STN_DATUM_CONVERSION`, `STN_OPERATION_SCHEDULE`, `STN_REGULATION`, `STN_REMARKS` (et codes
    `STN_*` associés) ;
  - Débits : `DLY_FLOWS`, `ANNUAL_STATISTICS`, `ANNUAL_INSTANT_PEAKS` ;
  - Niveaux : `DLY_LEVELS` ;
  - Sédiments : `SED_DLY_LOADS`, `SED_DLY_SUSCON`, `SED_SAMPLES`, `SED_SAMPLES_PSD` (+ codes) ;
  - Référentiels : unités, symboles, codes, `VERSION`.
- **Comptages par table** : dans `metadata/stations/hydat-schema.{json,txt}` et
  `registry/datasets/hydat-reference-20260717.yaml`.

## Limites

- Couverture hydrométrique **inégale** (stations actives vs abandonnées, séries de longueur
  variable, trous) — les critères d'inclusion (période, statut, complétude) relèvent de la
  couche `canonical/`, documentée séparément, jamais « devinés » ici.
- La sémantique précise des colonnes (unités, codes symboliques) est celle des PDFs de définition
  ECCC ; **aucune interprétation n'est ajoutée** dans ce dépôt tant qu'elle n'est pas explicitée
  par une transformation `canonical/` tracée.

## Procédure de mise à jour

1. Changer la release dans `config/project.yaml` (ou laisser la découverte dynamique).
2. Rejouer `nix develop -c ./scripts/bootstrap_reference.sh` — téléchargement + provenance +
  inspection + manifeste ; les anciennes releases restent **intactes** dans `data/raw/hydat/`.
3. Le manifeste dataset référence explicitement la release ; jamais de migration silencieuse.