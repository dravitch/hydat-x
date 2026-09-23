# HYDAT-X — ARCHITECTURE

**Référentiel expérimental indépendant** de contre-expertise des modèles de prévision du risque
d'inondation. La plateforme est prête **avant** de voir tout code candidat ; elle est conçue pour
reproduire, contrôler, challenger et comparer.

## Principe de séparation stricte des données

| Répertoire            | Rôle | Politique |
|-----------------------|------|-----------|
| `data/raw/`           | Téléchargements **gelés** à l'identique (ECCC), par release | **Jamais modifié**. Hashs dans `MANIFEST.sha256`, provenance YAML |
| `data/canonical/`     | Copies/transformations documentées, avec provenance saisie | Créées uniquement avec transformation + ID/version/source/hash + critères d'inclusion |
| `data/reference/`     | Artefacts de référence pour l'évaluation (targets, splits)  | Exploitables uniquement si issues d'un canonical traçable |

Règle : **rien n'entre en `canonical/` sans provenance documentée** ; **rien n'entre en
`reference/` sans identité** (dataset_id, version, source, hash, transformations, période,
population, critères d'inclusion).

## Couches

```text
data/raw/…                artefacts téléchargés (jamais modifiés)
metadata/downloads/       manifeste de provenance par téléchargement (YAML)
metadata/provenance/      captures SOUP et autres attestations d'environnement
metadata/stations/        schéma SQLite + inventaire des stations (json/txt/parquet/csv)
registry/datasets/        manifestes de datasets (dataset_id, hashes, comptages, période)
scripts/                  bootstrap + contrôle (reproductible)
config/                   configuration projet
docs/                     protocole, sources, provenance, décisions, rapport
```

## Chaîne de bootstrap (`scripts/bootstrap_reference.sh`)

1. **Découverte de release** — lecture de l'index ECCC ; release la plus récente par défaut
   (`hydat.sqlite3_<AAAAJJMM>`), verrouillable via `config/project.yaml`.
2. **Téléchargement atomique** — temp → validation (taille > 0, ZIP) → sha256 → `mv` atomique ;
   reprise si hash = manifeste ; conflit renommé `.conflict.*`, jamais écrasé.
3. **Provenance** — chaque artefact appendé à `metadata/downloads/hydat-<release>-download-manifest.yaml`
   (`artifact, source_url, retrieved_at_utc, filename, size_bytes, sha256, content_type,
   source_page, release`) ; sidecar `data/raw/hydat/<release>/MANIFEST.sha256` (une ligne/fichier).
4. **Environnement Python** — `uv sync --python 3.12` depuis `pyproject.toml` (venv `.venv`).
5. **Soup CLI** — périphérique de la couche évaluation/gating, installé via `uv tool install
   soup-cli --python 3.12` (hors des `[train]`), environnement capturé dans
   `metadata/provenance/soup-environment.txt`.
6. **Inspection lecture seule** — `inspect_hydat.py` : tables, colonnes, types, comptages,
   détection de la table de stations, période, inventaire stations (Parquet + CSV) ;
   la base SQLite n'est **jamais** modifiée.
7. **Manifeste dataset** — `make_manifest.py` : `registry/datasets/hydat-reference-<release>.yaml`,
   hash réel recalculé, aucune valeur non mesurée (`null` si inconnue).
8. **Test de santé** — `verify_environment.sh` : outils, imports Python, données, inspection,
   inventaire, provenance ; lignes `[PASS]/[FAIL]` ; exit non nul sur échec critique.

## Outillage

| Composant | Rôle |
|-----------|------|
| `flake.nix` + `flake.lock` | devShell reproductible (nixpkgs nixos-24.11, ref `50ab7937…`) |
| `uv` + `uv.lock` + `pyproject.toml` | dépendances Python gelées |
| `.envrc.example` | intégration direnv optionnelle |

L'isolation : la source de vérité du référentiel est ECCC ; tout le reste (metrics candidat,
data engineering de l'équipe évaluée) est extérieur et traité en **candidat**.