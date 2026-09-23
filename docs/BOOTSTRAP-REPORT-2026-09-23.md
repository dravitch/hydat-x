# BOOTSTRAP REPORT — 2026-09-23

Statut : **TERMINÉ — toutes les étapes du cycle de référence passent (EXIT 0, tous PASS).**

## Environnement

| Outil | Version | Où |
|-------|---------|----|
| OS | NixOS (store `/nix/store`) | hôte |
| nix | 2.34.8 | `/run/current-system/sw/bin/nix` |
| git | 2.47.2 | devShell |
| curl | 8.12.1 | devShell |
| unzip | 6.0 | devShell |
| jq | 1.7.1 | devShell |
| sqlite3 | 3.46.1 | devShell |
| duckdb | 1.1.3 | devShell |
| python | 3.12.8 | devShell `python312` / `.venv` |
| uv | 0.4.30 | devShell (uv.lock résolu) |
| soup-cli | 0.75.1 | uv tool `~/.local/bin/soup` |

Entrées verrouillées : nixpkgs `nixos-24.11` (`50ab7937…`), `fork`/inputs du `flake.lock`, deps
Python dans `uv.lock`.

## Acquisition de la source

- Index : `https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/` (HTTP 200)
- Release retenue : **20260717** (récupération réelle `2026-09-23T08:48Z` UTC)
- Base HYDAT **SQLite** + 4 PDF officiels (définitions EN/FR, notes de version EN/FR)
  archivés dans `data/raw/hydat/20260717/`.

| Artefact | Fichier final | Taille (octets) | SHA-256 |
|----------|---------------|-----------------|---------|
| Conteneur SQLite | `data/raw/hydat/20260717/sqlite/Hydat_sqlite3_20260717.zip` | 278 852 677 | `b05eb121a547ca4a179a27aa47c354089fd902e93e5dc1e4a5416fc4641eb298` |
| Base | `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` | 1 296 893 952 | `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517` |
| Définition EN | `documentation/HYDAT_Definition_EN.pdf` | 51 748 | `b3ab1954bf5aeedb026cebe939764fcfbda0266fb267cb6a7315544c9be8e1ee` |
| Définition FR | `documentation/HYDAT_Definition_FR.pdf` | 59 671 | `a74b0c8147f7e70587bf24bf05b124b2707e3fa8d4ae1cbca669ff69795a32b9` |
| Notes EN | `documentation/HYDAT_ReleaseNotes_20260717_EN.pdf` | 101 173 | `a9e481777fe635ff52a7630610578469a0e5bfc28b37bd927c933c6b894b3327` |
| Notes FR | `documentation/HYDAT_ReleaseNotes_20260717_FR.pdf` | 104 499 | `ab0f126e721ebdc453f15cc9c8a0bab73a615d3aae0bb4ae2758eaad036bc92c` |

Provenance par artefact : `metadata/downloads/hydat-20260717-download-manifest.yaml`
(+ sidecar `data/raw/hydat/20260717/MANIFEST.sha256`, dédupliqué).

## Contenu mesuré de la base (lecture seule)

- **33 tables**, **8 057 stations** (table `STATIONS`), période couverte **1850 → 2026**
  (bornes `STN_DATA_RANGE`).
- Débits : `DLY_FLOWS` 1 779 871 lignes ; Niveaux : `DLY_LEVELS` 840 225 ;
  Statistiques : `ANNUAL_STATISTICS` 201 916, `ANNUAL_INSTANT_PEAKS` 182 723 ;
  Sédiments : `SED_SAMPLES` 127 468, `SED_DLY_*` ~54k, `SED_SAMPLES_PSD` 218 534.
- Détail complet : `metadata/stations/hydat-schema.{json,txt}` ; inventaire stations :
  `metadata/stations/station-inventory.{parquet,csv}`.
- Manifeste dataset : `registry/datasets/hydat-reference-20260717.yaml`.

## Commandes exécutées

```bash
nix develop -c ./scripts/bootstrap_reference.sh   # découverte→téléchargement→provenance→venv→soup→inspect→manifeste→health
nix develop -c ./scripts/verify_environment.sh     # [PASS] sur les 16 contrôles + verdicts agrégés
nix develop -c python scripts/inspect_hydat.py --release 20260717
nix develop -c soup doctor                          # 1 issue (stack [train] absente) — attendu, non bloquant
```

Résultat du test de santé global : `HYDAT-X ENVIRONMENT: PASS`, `HYDAT REFERENCE: PASS`,
`SOUP CLI: PASS`, `SQLITE INSPECTION: PASS`, `STATION INVENTORY: PASS`, `PROVENANCE: PASS`.

## Problèmes rencontrés et résolutions

1. **numpy ne s'importe pas sous NixOS** (« import numpy from its source directory » = message
   trompeur ; réel : `libstdc++.so.6` absent) → devShell expose `LD_LIBRARY_PATH`
   (`stdenv.cc.cc.lib`/`zlib`). Résolution D4.
2. **Bug `append_prov $5`** : l'appel passait 4 arguments au lieu de 5 (sha256 manquait) → fix
   de ligne, puis reprise incrémentale (REUSE des artefacts déjà hashés).
3. **`soup --version` n'existe pas** → remplacé par la sous-commande `soup version`.
4. **Doublons dans `MANIFEST.sha256`** aux reprises → dédup `sort -u` (idempotence).
5. **Période non détectée initialement** (colonnes `YEAR/MONTH`, pas `DATE`) → dérivation via
   `STN_DATA_RANGE` (1850–2026).

## Décisions prises

Registre : `docs/DECISIONS.md` (D1–D9). Points structurants : SQLite > HYDEX/MDB ; release gelée
20260717 ; python ≤ 3.12 ; Soup hors `[train]` ; séparation RAW/CANONICAL/REFERENCE stricte.

## Reste à faire (hors périmètre 24 h)

- Couche `canonical/` (transformations documentées : critères de population, complétude,
  segmentation) et `reference/` (targets, splits) — par le protocole v0.1.
- Charge utile d'évaluation (metrics, calibration) et bancs baselines.
- Tout candidat venu de l'équipe évaluée sera traité comme un **objet à tester**, jamais comme
  une source du référentiel.