# Sources amont de HYDAT-X

Projet autonome 83-HYDAT-X. Index des documents dont la plateforme tire ses revendications, ses
définitions et ses contrôles. Toutes les entrées sont des références **amont** : HYDAT-X n'en
dépend naturellement pas pour ses données (celles-ci viennent d'ECCC, gelées par la couche
`data/raw/`), mais s'ancre sur leur analyse pour construire le protocole.

## 1. DELTA-5 — agent-1 : événements rares (EVT / PAC)

Rôle dans HYDAT-X : définition des événements extrêmes, traitement de la rareté, seuils de
queue — alimente le registre des définitions d'« inondation » et les challenges C3/C4.

- `81_DELTA-5/research/deepreview-cobaye-01/agent-1/claude-2026-09-20-agent1-evt-pac-axe-rarete.md`
- `81_DELTA-5/research/deepreview-cobaye-01/agent-1/qwen-2026-09-20-agent1-evt-pac-axe-rarete.md`
- `81_DELTA-5/research/deepreview-cobaye-01/synthese/agent1-synthese-audit-mathematique-axe-rarete.md`

## 2. Agent-5 : diagnostic technique HYDAT / AUC-ROC / ML

Rôle dans HYDAT-X : revendication à tester (AUC 0,95 ; 15 ans ; 2 000+ stations ; « données
inédites »), mécanismes non prévisionnels possibles (calendrier, persistance, fuite de
découpage, identité de station), contrôles négatifs requis, séparation HYDEX/HYDAT.

- `82_SCHEMA/missions/agent-5/agent5-diagnostic-hydat-auc-roc-ml.md`
- `82_SCHEMA/missions/agent-5/correctif-opus-diagnostic-hydat-auc-roc-ml.md`
- `82_SCHEMA/missions/agent-5/REVUE-CODEX.md`, `REVUE-CODEX-CLAUDE-DIAGNOSTIC.md`
- `82_SCHEMA/missions/agent-5/prompt-benchmark-hydat-hydex.md`
- `82_SCHEMA/missions/agent-5/{gemini,deepseek,qwen}-benchmark-hydat-hydex.md` (+ `*-review-*`)
- `81_DELTA-5/research/deepreview-cobaye-01/synthese/agent2-synthese-audit-technique-juridique-eccc.md` (architecture HYDEX/HYDAT, pipeline AQUARIUS)

## 3. Recommandations SCHEMA (rapport LIV01 rc3)

Rôle dans HYDAT-X : cadre de test que la plateforme opérationnalise — T1 (destinataire, décision
et valeur), T2 (portée réelle de la performance ; baselines calendrier, persistance, identité de
station ; règle de gain), T3 (passage archive-flux) ; proto-tests §13 ; registre des sources §17 ;
recommandations R8 (prévision vs reconnaissance) et R9 (NSRPS/GEM-Hydro comme comparateur).

- `82_SCHEMA/deliverables/LIV01/source-fr/rapport-final-SCHEMA-LIV01-rc3-fr.md`
- `82_SCHEMA/deliverables/LIV01/source-en/report-final-SCHEMA-LIV01-rc3-en.md`

## 4. Données ECCC (source de vérité, hors corpus)

- Archive nationale HYDAT — https://www.canada.ca/fr/environnement-changement-climatique/services/eau-apercu/volume/surveillance/releves/produits-donnees-services/archives-nationales-hydat.html
- Données temps réel HYDEX — https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html
- Readme officiel CaLDAS-NSRPS (registre NSRPS/GEM-Hydro) — https://eccc-msc.github.io/open-data/msc-data/nwp_caldas-nsrps/readme_caldas-nsrps_en