# HYDAT-X — DÉCISIONS (décisions de mise en œuvre)

Registre des décisions prises pendant le bootstrap. Convention : changements d'orientation
structurants → nouvelle entrée datée.

## 2026-09-23 — Bootstrap du référentiel

### D1. Source de données = archive HYDAT (SQLite), pas HYDEX ni MDB
La source de vérité est l'archive HYDAT d'ECCC (`Hydat_sqlite3_<release>.zip`). HYDEX (service de
consultation) est écarté comme source : exposition dépendante du moment de requête, non
reproductible. Le compagnon Access/MDB n'est pas téléchargé : SQLite préféré.

### D2. Release cible : 20260717 (gelée)
Découverte dynamique sur l'index ECCC ; release trouvée `20260717`. Elle est **gelée** dans les
manifestes ; rejouer le bootstrap avec une release plus récente se fait explicitement
(`config/project.yaml`).

### D3. python = 3.12 (maximum autorisé)
Contrainte Soup `>=3.10,<3.13` → `.venv` créé par `uv sync --python 3.12` ; nix `python312`
(CPython 3.12.8). Pas de torch/CUDA/conda/poetry.

### D4. DevShell Nix : `LD_LIBRARY_PATH` pour les wheels
Sous NixOS, l'import numpy échouait (`libstdc++.so.6: cannot open shared object file`, affiché
comme « import numpy from its source directory »). Le devShell expose désormais
`lib.makeLibraryPath [ stdenv.cc.cc.lib zlib ]`. Constaté : numpy 2.2.6/pandas 2.3.3 OK.

### D5. Soup CLI hors `[train]`
`uv tool install --python 3.12 soup-cli` (soup-cli 0.75.1). `soup doctor` signale « training stack
not installed » → **attendu**, non bloquant (mission sans entraînement).

### D6. Période de couverture dérivée de `STN_DATA_RANGE`
Bornes MIN/MAX de `YEAR_FROM`/`YEAR_TO` sur les lignes station/type → **1850–2026**. Les tables
de séries (`DLY_FLOWS`,…) servent de repli. La période est un fait mesuré, pas une hypothèse.

### D7. Hash de la base recalculé, jamais copié
`Hydat.sqlite3` (1 296 893 952 octets) → sha256 recalculé au moment du manifeste
(`dedupe` idempotent du sidecar `MANIFEST.sha256`).

### D8. Séparation RAW / CANONICAL / REFERENCE maintenue stricte
Le bootstrap ne remplit que `raw/` (gelé). Aucune écriture dans `canonical/`/`reference/` sans
provenance documentée (transformations + critères d'inclusion) — délibéré, à compléter plus tard.

### D9. Intégration de l'archive de référence CODEX
Copie de `82_SCHEMA/missions/REF-CODEX-HYDAT-X-plateforme-contre-expertise.md` dans
`docs/REF-CODEX-HYDAT-X-plateforme-contre-expertise.md` (la mission la référence en `docs/` du
dépôt). La référence source reste l'original côté SCHEMA.

## Règles conservées de la mission

- **Aucune valeur non mesurée** dans les manifestes (→ `null`) — pas de chiffres inventés.
- **Jamais d'écrasement silencieux** ; conflit → `*.conflict.<ts>`.
- **Aucune donnée « candidat »** introduite dans le référentiel ; tout candidat est un simple
  objet à tester contre lui.
- **Pas d'entraînement ML, pas de UI, pas de sophistication prématurée** à ce stade.