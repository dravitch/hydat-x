# HYDAT-X — Independent Flood Prediction Benchmark

**Projet autonome 83-HYDAT-X**, ancré dans le fil DELTA-5/SCHEMA. Référentiel expérimental
indépendant pour reproduire, contrôler, challenger et comparer les modèles de prévision du risque
d'inondation soumis à l'équipe, sans dépendre du code, des données préparées ni des métriques
produites par l'équipe évaluée.

La plateforme **s'appuie** sur :
- la documentation **agent-1** de DELTA-5 (`81_DELTA-5/research/deepreview-cobaye-01/agent-1/`, synthèse `synthese/agent1-…`) — mathématique des événements rares (EVT/PAC) ;
- la documentation **agent-5** (diagnostic technique HYDAT/AUC-ROC/ML, `82_SCHEMA/missions/agent-5/`) — mécanismes non prévisionnels, contrôles négatifs ;
- les **recommandations SCHEMA** (rapport LIV01 rc3, §9 T1/T2/T3, §13, R8/R9).

Pilotage (enregistré côté SCHEMA, chemin croisé vers ce projet) :
- Proposition source archivée : `82_SCHEMA/missions/REF-CODEX-HYDAT-X-plateforme-contre-expertise.md`
- Évaluation critique vs méthodologie rc3 : `82_SCHEMA/missions/eval-critique-CODEX-HYDAT-X-vs-rc3.md`
- Décision : `82_SCHEMA/decisions/ADR-004-referentiel-contre-expertise-HYDAT-X.md`
- Index des sources amont : `docs/SOURCES.md`

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
└── docs/            # SOURCES.md, protocoles, rapport
```

## Principe

> Nous ne cherchons pas une erreur ; nous déterminons si le résultat survit à des protocoles de
> plus en plus adversariaux.

**Chaque expérience reçoit un identifiant et un manifeste** : dataset exact, commit du code,
paramètres, période, stations, définition de l'événement, seed, métriques et artefacts.

**La plateforme doit être prête avant de voir le code du candidat.** Le premier livrable est le
`HYDAT-X Reference Protocol` (`docs/HYDAT-X-Reference-Protocol-v0.1.md`) ; une fois gelé, le
prototype soumis devient un simple candidat à tester contre le référentiel.