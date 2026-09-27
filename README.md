# HYDAT-X — Independent Flood Prediction Benchmark

**Projet autonome 83-HYDAT-X**, ancré dans le fil DELTA-5/SCHEMA. Référentiel expérimental
indépendant pour reproduire, contrôler, challenger et comparer les modèles de prévision du risque
d'inondation soumis à l'équipe, sans dépendre du code, des données préparées ni des métriques
produites par l'équipe évaluée.

> **Pour comprendre rapidement la thèse, les hypothèses et les données qui manquent à HYDAT seul :**
> ouvrir [`docs/HYDAT-X-PROJECT-SUMMARY.html`](docs/HYDAT-X-PROJECT-SUMMARY.html).

La plateforme **s'appuie** sur :
- la documentation **agent-1** de DELTA-5 (`81_DELTA-5/research/deepreview-cobaye-01/agent-1/`) — mathématique des événements rares (EVT/PAC) ;
- la documentation **agent-5** (diagnostic technique HYDAT/AUC-ROC/ML, `82_SCHEMA/missions/agent-5/`) — mécanismes non prévisionnels, contrôles négatifs ;
- les **recommandations SCHEMA** (rapport LIV01 rc3, §9 T1/T2/T3, §13, R8/R9).

Pilotage (enregistré côté SCHEMA, chemin croisé vers ce projet) :
- Proposition source archivée : `docs/REF-CODEX-HYDAT-X-plateforme-contre-expertise.md` (original : `82_SCHEMA/missions/REF-CODEX-HYDAT-X-plateforme-contre-expertise.md`)
- Évaluation critique vs méthodologie rc3 : `82_SCHEMA/missions/eval-critique-CODEX-HYDAT-X-vs-rc3.md`
- Décision : `82_SCHEMA/decisions/ADR-004-referentiel-contre-expertise-HYDAT-X.md`
- Index des sources amont : `docs/SOURCES.md`
- Protocole de référence v0.1 : `docs/HYDAT-X-Reference-Protocol-v0.1.md`

## Démarrage en 5 minutes

```bash
git clone <ce dépôt> 83_HYDAT-X && cd 83_HYDAT-X
nix develop                    # devShell reproductible (git, sqlite, duckdb, python 3.12, uv…)
./scripts/bootstrap_reference.sh   # télécharge + hashe + inspecte + manifeste + teste
./scripts/verify_environment.sh    # test de santé : 16 [PASS] attendus, exit 0
```

Si l'autorisation de l'installation dans `~/.local/bin` est simple : `uv tool install --python 3.12 soup-cli`
(voir `docs/SOUP.md`). Détails reproductibilité : `docs/REPRODUCIBILITY.md`.

## Arborescence

```text
83_HYDAT-X/
├── data/            # raw (gel ECCC), canonical (normalisé), reference (benchmark)
├── metadata/        # stations, downloads, provenance
├── benchmark/       # targets, splits, baselines, protocols
├── models/          # persistence, seasonal, statistical, ml
├── reproduction/    # candidate/ (TRACK-R)
├── challenge/       # temporal, geographic, extreme, leakage, lead_time
├── evaluation/      # metrics, calibration, reports
├── registry/        # datasets, experiments, evidence
├── config/          # project.yaml (release, paramètres)
├── scripts/         # bootstrap_reference.sh, inspect_hydat.py, make_manifest.py, verify_environment.sh
└── docs/            # protocole, sources, provenance, décisions, rapport
```

## Principe

> Nous ne cherchons pas une erreur ; nous déterminons si le résultat survit à des protocoles de
> plus en plus adversariaux.

**Chaque expérience reçoit un identifiant et un manifeste** : dataset exact, commit du code,
paramètres, période, stations, définition de l'événement, seed, métriques et artefacts.

**La plateforme doit être prête avant de voir le code du candidat.** Le premier livrable est le
`HYDAT-X Reference Protocol` (`docs/HYDAT-X-Reference-Protocol-v0.1.md`) ; une fois gelé, le
prototype soumis devient un simple candidat à tester contre le référentiel.

## État du référentiel (bootstrap 24 h — 2026-09-23)

- **Release HYDAT** : `20260717` (ECCC) — base SQLite + 4 PDF officiels archivés dans `data/raw/hydat/20260717/`, hashés (sidecar + provenance YAML).
- **Base inspectée lecture seule** : 33 tables, 8 057 stations, période 1850–2026 → `metadata/stations/`.
- **Manifeste dataset** : `registry/datasets/hydat-reference-20260717.yaml` ; **rapport** : `docs/BOOTSTRAP-REPORT-2026-09-23.md`.
- **Soup CLI** (hors `[train]`) opérationnel et capturé : `metadata/provenance/soup-environment.txt`.
- **Verrous** : nixpkgs 24.11 (`flake.lock`), `uv.lock`, python 3.12.

### Critères d'acceptation du bootstrap (24 h)

| # | Critère | État |
|---|---------|------|
| 1 | `nix develop` donne un shell fonctionnel (outils listés dispo) | ✅ constaté |
| 2 | `verify_environment.sh` → 16 `[PASS]`, exit 0 | ✅ constaté |
| 3 | Env Python 3.12 + deps (`uv sync`) | ✅ constaté |
| 4 | Base HYDAT SQLite téléchargée depuis l'index ECCC (release détectée dynamiquement) | ✅ `20260717` |
| 5 | Hash SHA-256 par artefact (sidecar + provenance) | ✅ 6 artefacts |
| 6 | Base jamais modifiée (inspection `mode=ro`) | ✅ |
| 7 | Schéma (tables/colonnes/comptages) + inventaire stations (Parquet/CSV) | ✅ 33 tables / 8 057 stations |
| 8 | Manifeste dataset généré (valeurs mesurées, pas de chiffres inventés) | ✅ |
| 9 | Soup CLI opérationnel, `[train]` non installé (volontaire), diagnostic capturé | ✅ une issue non bloquante |
| 10 | Aucune donnée candidat, aucun ML, aucune UI | ✅ |
| 11 | Bootstrap relançable et idempotent (REUSE) | ✅ |
| 12 | Rapport final avec valeurs mesurées | ✅ `docs/BOOTSTRAP-REPORT-2026-09-23.md` |
