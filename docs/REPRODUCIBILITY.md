# HYDAT-X — REPRODUCIBILITY

Objectif : une personne nouvelle obtient un environnement opérationnel complet avec deux
commandes, puis peut auditer **toutes** les étapes (versions, sources, hashs, comptages).

## Commandes de référence

```bash
nix develop                # entre dans le devShell (git, curl, unzip, sqlite, duckdb, python 3.12, uv…)
./scripts/bootstrap_reference.sh   # télécharge + valide + inspecte + manifeste + teste
./scripts/verify_environment.sh    # test de santé global (doit finir en PASS/exit 0)
python scripts/inspect_hydat.py    # inspection lecture seule (rapport JSON/TXT + inventaire)
soup doctor                        # diagnostic Soup CLI (hors stack [train], non bloquant)
```

## Verrous d'entrées

| Entrée | Verrou |
|--------|--------|
| Distribution Nix | `flake.lock` — nixpkgs `nixos-24.11`, commit `50ab793786d9de88ee30ec4e4c24fb4236fc2674` |
| Dépendances Python | `uv.lock` (résolu par uv au premier `uv sync`) |
| Python | 3.12 (nix `python312` = CPython 3.12.8 ; `.venv` créé par uv) |
| Release HYDAT | découverte dynamique de l'index ECCC ; verrouillable via `config/project.yaml` (par défaut : la plus récente au moment du bootstrap) |
| Soup CLI | version fixée par l'index uv au moment de l'installation (`soup-cli 0.75.1` constaté) |

## Version constatée au bootstrap (2026-09-23)

| Outil | Version | Provenance |
|-------|---------|-----------|
| nix | 2.34.8 | hôte (`/run/current-system/sw/bin/nix`) |
| git | 2.47.2 | nix devShell |
| curl | 8.12.1 | nix devShell |
| unzip | 6.0 | nix devShell |
| jq | 1.7.1 | nix devShell |
| sqlite3 | 3.46.1 | nix devShell |
| duckdb | 1.1.3 | nix devShell |
| python | 3.12.8 | nix `python312` / `.venv` |
| uv | 0.4.30 | nix devShell (l'hôte fournit uv 0.11.21 ; seule la version devShell compte pour la reproductibilité) |
| soup-cli | 0.75.1 | uv tool `~/.local/bin/soup` |

## Idempotence et reprises

- `bootstrap_reference.sh` est rejouable : tout fichier déjà présent avec un hash conforme au
  sidecar est **réutilisé** (log `REUSE`), jamais redescendu ni écrasé.
- Un fichier présent dont le hash diffère du manifeste est conservé sous `*.conflict.<timestamp>`
  puis re-téléchargé — jamais écrasé silencieusement.
- `MANIFEST.sha256` est dédupliqué (`sort -u`) — une ligne par fichier, quelle que soit l'histoire
  des reprises.
- La base SQLite est ouverte **lecture seule** (`mode=ro`) pour toute inspection.

## Notes spécifiques NixOS

- Les wheels PyPI (numpy 2.2.6, pandas, scipy, pyarrow…) exigent `libstdc++.so.6` et `zlib` :
  le devShell exporte `LD_LIBRARY_PATH` (fourni par `stdenv.cc.cc.lib`/`zlib`). Sans cela
  l'import numpy échoue avec l'erreur trompeuse « import numpy from its source directory »
  (message effectif : `libstdc++.so.6: cannot open shared object file`).
- Soup CLI et ses dépendances s'installent dans `~/.local/bin` (uv tool) — hors du store ; le
  PATH du devShell inclut `~/.local/bin`. Réinstallable à l'identique avec
  `uv tool install --python 3.12 soup-cli`.

## Limites de reproductibilité

- La disponibilité/version publiée de HYDAT évolue ; le gel **exact** de la release est
  l'engagement de ce dépôt (le manifeste + les hashs font foi, pas l'« index le plus récent »).
- L'état de `~/.local/bin` (soup) dépend d'une installation utilisateur : capturée dans
  `metadata/provenance/soup-environment.txt`, non transférable par le dépôt tel quel.