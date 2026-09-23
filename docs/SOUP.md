# HYDAT-X — SOUP (Software Of Unknown Provenance)

## Pourquoi SOUP ici

Soup (`soup-cli`, https://github.com/MakazhanAlpamys/Soup) est intégré comme **périphérique de la
couche évaluation/gating** du référentiel (diagnostic des modèles candidats, comparaisons côte à
côte), **sans la moindre fonctionnalité d'entraînement**. C'est la position adoptée par la
décision ADR-004 (82_SCHEMA) : opérationnaliser les recommandations, hors `[train]`.

## Installation reproductible

```bash
nix develop                                   # python 3.12 + PATH ~/.local/bin
uv tool install --python 3.12 soup-cli        # exécutable : ~/.local/bin/soup
```

- Version constatée au bootstrap : **soup-cli 0.75.1** (27 paquets résolus par uv).
- Contrainte respectée : Python **≤ 3.12** (paquet pyproject : `>=3.10,<3.13`).

## Diagnostic constaté (2026-09-23, capture `metadata/provenance/soup-environment.txt`)

| Élément | Résultat |
|---------|----------|
| `soup version` | OK (soup-cli 0.75.1) |
| `soup --help` | OK — commandes disponibles dont `init/train/cost/push/merge/diff/infer…` |
| `soup doctor` | **1 « issue »** : *Training stack not installed* (`pip install "soup-cli[train]"`) |
| Backend | `unknown (torch not installed)` |
| Dépendances requises de base | `pyyaml OK`, `plotext OK`, `httpx OK` ; optionnelles `[train]` (torch, transformers, …) **non installées** — **volontaire** |

## Position

- L'issue `soup doctor` (stack d'entraînement absente) est **non bloquante** et **conforme à la
  mission** : aucun entraînement de LLM n'est requis ni autorisé dans HYDAT-X.
- Aucun extra `[train]` n'est installé ; si un jour l'équipe candidate exigait ce mode, la
  décision devra être documentée en `docs/DECISIONS.md` avant toute activation.

## Traçabilité

- Capture de l'environnement : `metadata/provenance/soup-environment.txt` (régénérée à chaque
  bootstrap).
- Attestation : `soup` présent à `~/.local/bin/soup` ; l'installation utilisateur est documentée
  comme limite de reproductibilité (voir `docs/REPRODUCIBILITY.md`).