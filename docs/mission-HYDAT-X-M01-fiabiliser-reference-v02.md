# MISSION — `HYDAT-X-M01` — Fiabiliser les données dérivées avant le gel v0.2

> **Statut : FICHE PRESCRIPTIVE, NON EXÉCUTÉE.** Ce document autorise et encadre un travail ;
> il ne prouve aucun correctif. Le journal probant doit être créé séparément au démarrage.

## 0. Métadonnées

| Champ | Valeur |
|---|---|
| Mission ID | `HYDAT-X-M01` |
| Date de création | `2026-09-24` |
| Auteur / planificateur | Codex, à partir de `AUDIT-HYDAT-X-001` |
| Exécutant prévu | Agent d'implémentation HYDAT-X, avec revue humaine des décisions scientifiques |
| Projet | `83_HYDAT-X` |
| Statut initial | `PRÊTE` |
| Priorité | Bloquante |
| Type | Code, données, tests, documentation et gouvernance |
| Dépend de | Baseline auditée; base HYDAT `20260717`; décisions D1–D6 laissées ouvertes |
| Bloque | Gel du protocole v0.2, génération reference, entraînement B0–B5, réception d'un candidat |
| Source de vérité | `docs/AUDIT-HYDAT-X-001.md`, findings `F-01` à `F-08` |
| Journal attendu | `docs/mission-HYDAT-X-M01-journal.md` |

### 0.1 Baseline exigée

| Élément | Exigence | Comment la vérifier avant action |
|---|---|---|
| Dépôt / corpus | `/home/andrei/Projects/83_HYDAT-X` | `pwd`; vérifier la racine Git |
| Branche / tag | Branche explicitement choisie; ne pas supposer `main` | `git branch --show-current`; `git show-ref` |
| Commit de départ | À résoudre; baseline d'audit : `561e630d60b70bc697067e64a9c90aebeb0e6b05` + worktree | `git rev-parse HEAD` |
| État du worktree | Modifications admises uniquement si inventoriées et préservées; le chantier REFERENCE-01 est actuellement non commité | `git status --short`; enregistrer la liste dans le journal |
| Environnement | `nix develop`, `flake.lock`, `uv.lock`, Python 3.12 | `nix develop -c ./scripts/verify_environment.sh` |
| Artefacts d'entrée | SQLite `20260717` hash `9185ea30…ef517`; rapports DATA-AUDIT-001; protocoles draft | Recalculer le SHA-256; ne pas recopier le présent document |

**Règle d'arrêt :** si les changements préexistants chevauchent les fichiers ciblés sans pouvoir
être attribués ou préservés, arrêter et consigner le blocage. Ne jamais effacer les artefacts
actuels avant d'avoir conservé une baseline comparable.

### 0.2 Portée d'autorisation

| Action | Autorisée par cette mission ? | Approbation supplémentaire |
|---|---|---|
| Lecture et diagnostic | Oui | Aucune |
| Modification des scripts, tests, protocoles et docs ciblés | Oui | Aucune, dans le workspace |
| Création de fixtures, tests et probes | Oui | Aucune; données minimales sans secret |
| Régénération des artefacts DATA-AUDIT-001 | Oui, après tests ciblés | Conserver les preuves avant/après |
| Commit / tag | Non | Demande explicite de l'utilisateur |
| Réseau / service externe | Non requis | Accord si un nouveau téléchargement devient nécessaire |
| Gel/publication du protocole v0.2 | Non | Validation humaine explicite D1–D6 |
| Suppression irréversible des anciens artefacts | Non | GO explicite; préférer archivage/version suivante |

## 1. Contexte

### 1.1 Problème observé

L'audit `AUDIT-HYDAT-X-001` a démontré que la segmentation T1/T4 agrège des observations
séparées par des lacunes calendaires. Il a aussi constaté une dérivation canonical réutilisée
sans identité de source, trois cibles `refhalf` annoncées mais absentes, des règles de split
incompatibles, quatre chemins de manifeste faux, un risque d'écrasement dans le bootstrap, un
ratio de couverture mal nommé et l'absence de tests métier.

Ces faits sont distincts des décisions scientifiques D1–D6 : ils doivent être corrigés ou
explicitement résolus avant de demander ces décisions et avant tout gel.

### 1.2 Pourquoi maintenant

Les sorties actuelles alimentent déjà `TARGET-DESIGN-001`, le protocole v0.2-draft et les
propositions de baselines. Geler le protocole avant correction transformerait une exploration
révisable en contrat erroné et obligerait à migrer les cibles, splits et comparaisons ultérieures.

### 1.3 État actuel connu

- **Acquis :** base brute hashée et lisible; environnement Nix fonctionnel; 16 contrôles de santé; pipeline d'audit explicite; protocoles au statut draft.
- **Défectueux ou manquant :** continuité des runs, lignée du cache, trois cibles refhalf, tests métier, chemins du manifeste, contrats de split.
- **Inconnu :** nouveaux comptages après correction; impact sur les runs extrêmes; population exacte sous le bon dénominateur; choix humains D1–D6.
- **Hypothèses de travail :** une lacune doit couper un run strictement consécutif; les régimes temporel et géographique sont deux évaluations séparées; toute dérivation doit porter le hash de sa source.

### 1.4 Dépendances et contrats à préserver

| Contrat / consommateur | Risque de rupture | Vérification exigée |
|---|---|---|
| Base HYDAT brute | Modification ou remplacement | Hash avant/après identique; ouverture lecture seule |
| Schéma des rapports CSV/JSON | Consommateurs documentaires cassés | Test de colonnes et versionnement des changements |
| IDs de target | Collision ou renommage silencieux | Registre unique; mapping avant/après explicite |
| Protocole v0.2-draft | Affirmations désynchronisées | Contrôle croisé YAML/Markdown/artefacts |
| Worktree utilisateur | Perte de travail non commité | Inventaire initial/final; aucun reset/checkout destructif |
| Reproductibilité Nix | Tests uniquement valides sur l'hôte | Toutes les validations finales dans `nix develop` |

## 2. Objectif général

> Produire depuis la base HYDAT hashée un audit régénérable dont les événements sont
> calendriquement continus, les dérivations et cibles sont manifestées, et les contrats de
> provenance et de split sont vérifiés par des tests discriminants, sans geler v0.2.

## 3. Objectifs détaillés

1. Reproduire F-01 par fixture, corriger la segmentation et régénérer les résultats affectés.
2. Introduire une identité de dérivation canonical liée au hash source, au code et aux paramètres.
3. Générer et manifester les quatre cibles `refhalf` proposées, ou retirer explicitement toute cible non produite.
4. Séparer les protocoles temporal-known-stations et geographic-unseen-stations avec invariants vérifiables.
5. Corriger chemins, sélection de release et comportement sans sidecar du bootstrap/manifeste.
6. Aligner le ratio de couverture, les rapports et les statuts avec les calculs réellement exécutés.
7. Installer et exécuter une suite de tests métier positive et négative dans la voie Nix officielle.

### 3.1 Hors objectifs

- décider si `0.0` sans symbole est manquant ou zéro réel ;
- choisir un seuil absolu T2 ou une source réglementaire ;
- valider humainement D1–D6 ;
- geler, taguer ou publier v0.2 ;
- entraîner B0–B5 ou évaluer un candidat ;
- prouver une performance hydrologique opérationnelle.

### 3.2 Portées de décision séparées

| Portée | Ce que la mission peut démontrer | Ce qu'elle ne démontre pas |
|---|---|---|
| Données dérivées | Lignée, déterminisme, invariants calendaires | Validité hydrologique des seuils |
| Protocole draft | Cohérence interne et matérialisation des splits | Approbation humaine ou gel |
| Bootstrap | Non-écrasement sur fixtures et chemins cohérents | Disponibilité future du serveur ECCC |
| Tests | Détection des défauts couverts | Absence de tout défaut inconnu |
| Audit régénéré | Chiffres obtenus par le pipeline corrigé | Performance d'un modèle candidat |

## 4. Protocole de validation

### 4.1 Baseline avant changement

| Mesure / probe | Résultat initial attendu | Preuve à conserver |
|---|---|---|
| Fixture `[J1 excès, J3 excès]` sans J2 | Un seul run erroné sur la baseline | Test rouge et sortie SQL |
| Comparaison `span != dur` sur événements actuels | 564 T1-q095-refhalf; 211 T1-q099-refhalf | CSV de synthèse avant correction |
| Cache présent avec mauvais hash source | Réutilisé à tort | Probe isolée hors données brutes |
| Vérification des chemins `raw_artifacts` | 4 PDF manquants au chemin manifesté | Sortie chemin/existence |
| Fichier cible préexistant sans sidecar | Risque de remplacement | Fixture temporaire, jamais sur les données réelles |
| Inventaire des cibles proposées | Trois artefacts refhalf absents | Liste fichiers + registre |
| Suite pytest | Absente/non exécutable actuellement | Sortie initiale |

### 4.2 Métriques avant / après

| Métrique | Baseline | Cible | Méthode de mesure |
|---|---:|---:|---|
| Runs avec `span != dur` sous continuité stricte | Non nul; valeurs connues ci-dessus | 0 | Analyse des CSV régénérés |
| Chemins manifestés inexistants | 4 | 0 | Vérification de chaque entrée |
| Cibles refhalf proposées et matérialisées | 1/4 | 4/4, ou registre réduit honnêtement | Contrôle registre ↔ fichiers ↔ hashes |
| Tests métier | 0 exécuté | Tous exécutés, 0 échec, skips justifiés | `pytest` dans Nix |
| Dérivations sans hash source/code | 1 cache majeur | 0 | Validation de manifeste |
| Règles de split contradictoires | 1 règle globale | 2 régimes séparés et testés | Tests d'intersection station/date |

Les nouveaux nombres d'événements sont à mesurer; aucune cible chiffrée ne doit être inventée.

### 4.3 Tests discriminants

| Risque | Test positif | Test négatif / mutation | Résultat exigé |
|---|---|---|---|
| Fusion à travers une lacune | Jours consécutifs au-dessus du seuil forment un run | Jour absent entre deux excès | Deux runs, ou règle explicite paramétrée |
| Cache étranger | Cache au bon hash est réutilisé | Hash source/code modifié | Rejet ou rebuild |
| Manifeste incomplet | Tous les chemins/hashes valides | Entrée inexistante ou hash faux | Échec non nul |
| Écrasement brut | Artefact conforme réutilisé | Artefact sans sidecar ou hash divergent | Original conservé sous nom de conflit |
| Sélection release | Liste ordonnée | Index fixture désordonné | Release numérique maximale sélectionnée |
| Split temporel | Même station autorisée sur dates disjointes selon régime | Chevauchement temporel interdit | Détection du chevauchement |
| Split géographique | Ensembles station disjoints | Station injectée des deux côtés | Détection de l'intersection |
| Target leakage | Seuil entraînement/reference accepté | Seuil whole-series marqué évaluation | Rejet |

### 4.4 Scénarios de panne ou de concurrence

| Fenêtre / scénario | État à préserver | Comportement attendu après reprise |
|---|---|---|
| Interruption pendant construction parquet | Ancien artefact valide ou aucun artefact publié | Temporaire ignoré; rebuild déterministe |
| Interruption pendant publication d'un manifeste | Manifeste précédent intact | Écriture temporaire puis remplacement atomique |
| Artefact brut local sans sidecar | Fichier original intact | Mise en conflit avant téléchargement |
| Deux audits simultanés sur le même cache | Aucun parquet partiel publié | Verrou ou sorties isolées par run |

### 4.5 Validation finale

| Contrôle | Commande / méthode | Seuil de succès |
|---|---|---|
| Tests ciblés | `nix develop -c python -m pytest tests/... -q` | 0 échec; tests négatifs observés |
| Suite complète | `nix develop -c python -m pytest -q` | 0 échec; skips explicités |
| Santé environnement | `nix develop -c ./scripts/verify_environment.sh` | 16 PASS, code 0 |
| Audit complet | `nix develop -c python scripts/audit_hydat.py` | Code 0, hash source confirmé |
| Cohérence | Validateur registre/manifeste/docs | 0 chemin absent, 0 target orpheline |
| Qualité Git | `git diff --check`; revue du diff | Code 0; aucun changement hors portée |
| Reproductibilité | Rebuild après déplacement/invalidaton contrôlée du cache | Hashes identiques pour mêmes entrées |

## 5. Procédure et gates d'exécution

### Partie A — Préparation et provenance

- lire intégralement l'audit, les scripts et protocoles ciblés ;
- résoudre la baseline et enregistrer l'état Git initial ;
- créer `docs/mission-HYDAT-X-M01-journal.md` avec statut `ACTIVE` ;
- préserver les sorties DATA-AUDIT-001 comme preuve avant changement ;
- recalculer le hash de la base brute et interdire toute écriture sur celle-ci.

### Partie B — Reproduction et mesures initiales

- créer des fixtures minimales pour continuité, cache, manifeste et bootstrap ;
- obtenir les échecs attendus sur la baseline ;
- enregistrer séparément pass, fail, skip et non exécuté ;
- confirmer les comptes de runs affectés sans modifier les artefacts publiés.

**Gate B :** si F-01 n'est pas reproduit, ne pas corriger la segmentation selon une hypothèse.
Consigner la divergence et demander un réexamen de l'audit.

### Partie C — Exécution

1. Corriger la continuité des runs et ajouter les tests.
2. Versionner la transformation daily canonical et son manifeste.
3. Corriger couverture et produire les quatre targets de référence.
4. Formaliser et tester séparément les deux familles de splits.
5. Durcir bootstrap et génération/vérification des manifestes.
6. Régénérer les sorties dans un nouvel emplacement ou avec sauvegarde explicite.
7. Mettre à jour les documents uniquement depuis les artefacts régénérés.

### Partie D — Vérification

- rejouer tous les tests et probes de baseline ;
- comparer nombres, hashes et schémas avant/après ;
- vérifier qu'aucun résultat `whole-series` n'est utilisé pour l'évaluation ;
- exécuter l'audit complet depuis un cache absent puis depuis un cache valide ;
- vérifier le diff et consigner toute limite résiduelle.

### Partie E — Gel v0.2, action à fort impact

**Point d'arrêt obligatoire :** la mission prépare un dossier proposant le gel, mais ne change
pas `status: draft`, ne crée pas de tag et ne publie pas de release.

Après A–D, présenter au décideur : résultats avant/après, nouveaux comptages, D1–D6, hashes et
rapport de réaudit. Attendre le texte explicite **« GO POUR GEL v0.2 »** avant toute opération
de gel, qui devra idéalement faire l'objet d'une mission distincte.

## 6. Instructions à l'exécutant

1. Reproduire chaque finding avant de le corriger.
2. Ne jamais modifier la base SQLite ou effacer silencieusement les sorties précédentes.
3. Préserver les changements non committés de l'utilisateur.
4. Ne pas remplacer `refhalf` par `whole` pour obtenir un artefact.
5. Ne pas imposer une décision D1–D6 sous couvert de correction technique.
6. Ne pas affaiblir un test ni modifier un seuil attendu sans consigner la décision.
7. Tout nombre documentaire doit être généré ou recalculable depuis un artefact identifié.
8. Séparer clairement tests de santé, tests métier et validation scientifique.
9. Laisser la mission ouverte si une cible, un manifeste ou un test bloquant manque.

## 7. Critères de succès

| ID | Critère observable | Bloquant ? | Statut initial | Preuve exigée |
|---|---|---|---|---|
| CS-01 | Une lacune calendaire coupe un run; tous les événements stricts vérifient `span == dur` | Oui | `NON ÉVALUÉ` | Tests + analyse sorties |
| CS-02 | Chaque dérivation porte et vérifie hash source, code, paramètres et sortie | Oui | `NON ÉVALUÉ` | Manifeste + mutation rejetée |
| CS-03 | Le registre et les artefacts contiennent exactement les mêmes quatre cibles refhalf proposées | Oui | `NON ÉVALUÉ` | Validateur + hashes |
| CS-04 | Splits temporel et géographique sont séparés et satisfont leurs invariants | Oui | `NON ÉVALUÉ` | Tests de disjonction |
| CS-05 | Tous les chemins du manifeste existent et leurs hashes concordent | Oui | `NON ÉVALUÉ` | Vérificateur non nul sur défaut |
| CS-06 | Bootstrap conserve tout fichier préexistant non attesté et choisit explicitement la dernière release | Oui | `NON ÉVALUÉ` | Fixtures négatives |
| CS-07 | Couverture calculée correspond au libellé et aux règles de population | Oui | `NON ÉVALUÉ` | Tests de stations à bords manquants |
| CS-08 | Suite métier passe dans Nix avec 0 échec et skips justifiés | Oui | `NON ÉVALUÉ` | Sortie pytest |
| CS-09 | Audit complet régénéré depuis la base hashée et cache vide | Oui | `NON ÉVALUÉ` | Journal, hashes, code 0 |
| CS-10 | Documentation ne revendique ni gel, ni validation humaine, ni capacité non prouvée | Oui | `NON ÉVALUÉ` | Revue croisée docs/YAML |
| CS-11 | Base brute inchangée | Oui | `NON ÉVALUÉ` | SHA-256 avant/après identique |
| CS-12 | Rapport de réaudit relie chaque F-01…F-08 à une preuve de fermeture ou le laisse ouvert | Oui | `NON ÉVALUÉ` | Addendum ou nouvel audit |

### Règle de clôture

- `CLÔTURÉE` : CS-01 à CS-12 sont tous prouvés sur la baseline finale ;
- `PARTIELLE` : des livrables existent, mais un critère bloquant reste non atteint ;
- `BLOQUÉE` : une dépendance ou autorisation empêche toute progression utile ;
- `ANNULÉE` : objectif retiré explicitement ;
- `OUVERTE` : exécution ou observation encore en cours.

La validation humaine D1–D6 n'est pas un critère de clôture de M01 : M01 doit fournir les
preuves corrigées permettant cette décision, sans la prendre.

## 8. Interdictions spécifiques

- modifier, réécrire ou « nettoyer » `data/raw/hydat/20260717/sqlite/Hydat.sqlite3` ;
- supprimer les anciens rapports sans archive et mapping de provenance ;
- considérer `verify_environment.sh` comme une suite de tests métier ;
- calculer B0 sur TEST/HOLDOUT ou utiliser une cible `whole-series` en évaluation ;
- masquer une baisse ou hausse des comptes après correction ;
- passer le protocole à `frozen`, committer, taguer ou publier sans autorisation séparée.

## 9. Livrables et format attendu

| Livrable | Emplacement | Contenu minimum | Autoritaire ? |
|---|---|---|---|
| Journal | `docs/mission-HYDAT-X-M01-journal.md` | Baselines, commandes, résultats, critères réels | Oui pour l'exécution |
| Tests métier | `tests/` | Fixtures et tests positifs/négatifs F-01/F-02/F-04/F-05/F-06 | Oui pour non-régression |
| Pipeline corrigé | `scripts/` | Segmentation, manifeste, cache et vérificateurs | Oui |
| Manifeste canonical | `registry/datasets/` | Source/code/paramètres/sortie hashés | Oui |
| Audit régénéré | Nouvel ID ou version explicitement reliée à DATA-AUDIT-001 | Résultats, schémas, hashes, comparaison | Oui |
| Artefacts target | `benchmark/targets/` et/ou `data/reference/` | Quatre targets refhalf manifestées | Oui après décision humaine |
| Protocoles corrigés | `benchmark/protocols/` et `docs/` | Deux splits, horizons et statuts cohérents | Oui tant que draft |
| Réaudit | `docs/AUDIT-HYDAT-X-001-ADDENDUM-01.md` ou audit suivant | État indépendant F-01…F-08 | Oui pour passage au gel |

### 9.1 Condition de handoff

La mission suivante de gel peut démarrer seulement avec un worktree attribuable, une base brute
au hash inchangé, un pipeline vert depuis cache vide, quatre cibles refhalf manifestées, deux
régimes de split testés et un réaudit sans finding bloquant. Le statut doit rester `draft`
jusqu'au GO humain explicite sur D1–D6.
