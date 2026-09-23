# HYDAT-X — DATA PROVENANCE

La provenance est **non négociable** : tout artefact du référentiel doit être traçable jusqu'à sa
source, avec une intégrité vérifiable, sans jamais être écrasé silencieusement.

## Enregistrement par artefact

Chaque téléchargement est consigné dans `metadata/downloads/hydat-<release>-download-manifest.yaml` :

```yaml
- artifact: "HYDAT_Definition_EN.pdf"
  source_url: "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/HYDAT_Definition_EN.pdf"
  retrieved_at_utc: "2026-09-23T08:57:38Z"
  filename: "HYDAT_Definition_EN.pdf"
  size_bytes: 51748
  sha256: "b3ab1954bf5aeedb026cebe939764fcfbda0266fb267cb6a7315544c9be8e1ee"
  content_type: "application/pdf"
  source_page: "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/"
  release: "20260717"
```

L'**heure de récupération** (`retrieved_at_utc`) est celle du téléchargement réel : elle appartient
à l'histoire de l'artefact, pas au moment où le rapport est écrit.

## Intégrité

- Sidecar `data/raw/hydat/<release>/MANIFEST.sha256` — une ligne `hash  filename` par fichier
  (dédupliqué, `sort -u`).
- Le hash de la base SQLite **n'est jamais copié depuis une source** : il est recalculé à chaque
  manifeste (`make_manifest.py`).
- Étapes de validation : taille > 0, intégrité ZIP (`unzip -t`) avant extraction, vérification
  des types MIME depuis les en-têtes de réponse.

## Chaîne de confiance — référence de données

| Niveau | Fichier | Contenu | Écrit par |
|--------|---------|---------|-----------|
| Téléchargement | `metadata/downloads/hydat-<release>-download-manifest.yaml` | par artefact (URL, UTC, taille, sha256, type, release) | `bootstrap_reference.sh` |
| Sidecar brut | `data/raw/hydat/<release>/MANIFEST.sha256` | hash du fichier brut à l'arrivée | `bootstrap_reference.sh` |
| Schéma/inventaire | `metadata/stations/hydat-schema.{json,txt}`, `station-inventory.{parquet,csv}` | structure de la base + stations, lecture seule | `inspect_hydat.py` |
| Dataset | `registry/datasets/hydat-reference-<release>.yaml` | dataset_id, source, release, artefacts bruts, hash db, comptages, période, statut | `make_manifest.py` |

## Règles d'or

1. **Jamais d'écrasement** : un fichier présent avec hash conforme → `REUSE` ; hash divergent →
   renommage `*.conflict.<ts>` puis re-téléchargement.
2. **Jamais de modification du RAW** : la base est ouverte en `mode=ro` ; aucune écriture dans
   `data/raw/` après le `mv` atomique.
3. **Aucune valeur non mesurée** : en cas de donnée indisponible → `null`, jamais de valeur
   « devinée » (mission : *do not invent numbers*).
4. **Séparation RAW / CANONICAL / REFERENCE** : l'entrée en `canonical/` exige une transformation
   documentée (ID, version, source, hash d'entrée, transformation, période, population, critères
   d'inclusion).

## État de référence (release 20260717, gelée le 2026-09-23)

| Artefact brut | Taille (octets) | SHA-256 |
|---------------|-----------------|---------|
| `Hydat_sqlite3_20260717.zip` | 278 852 677 | `b05eb121…1eb298` |
| `HYDAT_Definition_EN.pdf` | 51 748 | `b3ab1954…8e1ee` |
| `HYDAT_Definition_FR.pdf` | 59 671 | `a74b0c81…a32b9` |
| `HYDAT_ReleaseNotes_20260717_EN.pdf` | 101 173 | `a9e48177…b3327` |
| `HYDAT_ReleaseNotes_20260717_FR.pdf` | 104 499 | `ab0f126e…bc92c` |
| `Hydat.sqlite3` (extrait) | 1 296 893 952 | `9185ea30…ef517` |

Source : `https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/` (ECCC).