# Audit indépendant — HYDAT-X avant gel du protocole v0.2

## 0. Identité de l'audit

| Champ | Valeur |
|---|---|
| Identifiant | `AUDIT-HYDAT-X-001` |
| Cible auditée | Dépôt `83_HYDAT-X`, bootstrap, audit HYDAT et protocole v0.2-draft |
| Type | Audit initial ciblé de maturité et de reproductibilité |
| Question de décision | Le référentiel HYDAT-X peut-il être gelé en v0.2 et servir de base à une comparaison de modèles ? |
| Auditeur | Codex, audit indépendant en lecture seule de la cible |
| Commanditaire | Utilisateur du dépôt HYDAT-X |
| Début / fin | `2026-09-24 08:00 EDT` / `2026-09-24 08:14 EDT` |
| Référentiel | Architecture et règles internes HYDAT-X, protocoles v0.1/v0.2-draft, templates d'audit du dépôt |
| Rapport précédent | `docs/REFERENCE-01-REPORT.md` |
| Verdict précédent | `DATA UNDERSTOOD`, protocole v0.2 draft à geler après décisions D1–D6 |

### 0.1 Baseline immuable

| Élément | Valeur résolue par l'auditeur | Méthode de résolution |
|---|---|---|
| Dépôt ou corpus | `/home/andrei/Projects/83_HYDAT-X` | `pwd`, inspection directe |
| Branche | `main` | `git branch --show-current` |
| Tag demandé | N/A | Aucun tag demandé |
| Commit / version réellement auditée | `561e630d60b70bc697067e64a9c90aebeb0e6b05` + worktree non commité | `git rev-parse HEAD`, `git status --short` |
| Hash du paquet de preuve | Base HYDAT : `9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517` | `sha256sum data/raw/hydat/20260717/sqlite/Hydat.sqlite3` |
| État de travail initial | Sale : `flake.nix` modifié et 16 ensembles de fichiers non suivis, dont protocole, audit, rapports et templates | `git status --short` |
| État de travail final | Sale : état initial préservé, plus les deux documents demandés par l'utilisateur | `git status --short` à la clôture |
| Éléments exclus | Exactitude scientifique externe des conventions ECCC; performance de modèles candidats; décisions humaines D1–D6 | Hors autorisation et/ou sans candidat |

La baseline est résolue sans ambiguïté comme un couple commit + worktree. Les constats portant
sur REFERENCE-01 s'appliquent aux fichiers non suivis présents pendant l'audit et non au seul
commit `561e630`.

## 1. Mandat, périmètre et interdictions

### 1.1 Objectif principal

> Déterminer si les calculs, artefacts, contrôles et affirmations actuellement présents suffisent
> à geler le protocole v0.2 sans propager une cible erronée ou une provenance incomplète.

### 1.2 Sous-questions

1. Les sorties d'audit et les cibles correspondent-elles aux définitions annoncées ?
2. La provenance et les caches permettent-ils un rejeu non ambigu depuis la base gelée ?
3. Les règles de split, fuite et baseline sont-elles cohérentes et exécutables ?
4. Les affirmations de maturité sont-elles soutenues par des tests discriminants ?

### 1.3 Dans le périmètre

- scripts de bootstrap, inspection, manifeste, audit et vérification ;
- données et artefacts locaux de la release HYDAT `20260717` ;
- protocoles, définitions de cibles, rapports et documentation de reproductibilité ;
- état Git et environnement Nix/Python présents.

### 1.4 Hors périmètre

- téléchargement à nouveau de la base ECCC ;
- validation hydrologique externe de la politique des zéros ;
- entraînement de baselines ou de modèles candidats ;
- modification des scripts ou régénération complète de l'audit de 285 secondes ;
- arbitrage humain D1–D6 et gel effectif du protocole.

### 1.5 Interdictions faites à l'auditeur

- ne pas modifier la cible auditée pour faire disparaître un constat ;
- ne pas assimiler les 16 contrôles d'environnement à des tests de correction métier ;
- ne pas créditer les cases cochées du rapport sans inspection des artefacts ;
- ne pas déclarer valides les cibles `refhalf` qui ne sont pas produites ;
- ne pas confondre disponibilité de la base brute et benchmark exécutable.

## 2. Règles de preuve

### 2.1 Hiérarchie

1. preuve dynamique rejouée dans `nix develop` ;
2. code, base et artefacts primaires inspectés directement ;
3. rapports et documentation cohérents avec ces artefacts ;
4. déclaration non reproduite ;
5. élément non vérifiable dans ce mandat.

### 2.2 Statuts d'une affirmation

| Statut | Signification |
|---|---|
| `CONFIRMÉE` | Soutenue par une preuve recevable dans le périmètre. |
| `PARTIELLE` | Soutenue en partie, avec une réserve matérielle. |
| `CONTREDITE` | Une preuve directe démontre qu'elle est fausse sur la baseline. |
| `NON_VÉRIFIABLE` | Artefact, accès ou rejeu requis absent. |
| `HORS_PÉRIMÈTRE` | Le mandat ne permet pas de la trancher. |

### 2.3 Règles de comptage

- Les 16 contrôles du script de santé sont comptés séparément des tests métier.
- La compilation Python et le parsing YAML/JSON prouvent la lisibilité, pas la justesse.
- `pytest` est déclaré comme extra mais absent de l'environnement courant ; aucun test métier
  n'a donc été compté comme réussi.
- Les événements affectés par une lacune sont comptés depuis les CSV existants en comparant
  `end_dte - start_dte + 1` à `dur`.

## 3. Méthode et reproductibilité

### 3.1 Environnement

| Élément | Valeur |
|---|---|
| Système / architecture | Linux `6.18.50`, `x86_64` |
| Environnement reproductible | Nix flake + `flake.lock`, `uv.lock`, `.venv` Python 3.12.8 |
| Versions d'outils | Nix 2.34.8; Python 3.12.8; versions détaillées dans `docs/REPRODUCIBILITY.md` |
| Accès réseau | Non utilisé pour l'audit |
| Identifiants ou données réelles | Base publique HYDAT locale, release `20260717` |
| Contraintes de l'hôte | Workspace inscriptible; outils natifs Python disponibles correctement dans `nix develop` |

### 3.2 Procédure réellement exécutée

| # | Commande ou contrôle | Résultat brut conservé à | Code / état |
|---:|---|---|---|
| 1 | Inventaire Git, fichiers, tailles et historique | Git et présent rapport | Succès |
| 2 | Lecture des scripts, protocoles, rapports et manifestes | Fichiers sources cités | Succès |
| 3 | `nix develop -c ... ./scripts/verify_environment.sh` | Sortie de session; script rejouable | 16 PASS, code 0 |
| 4 | `python -m py_compile scripts/*.py` | Sortie de session | Code 0 |
| 5 | Parsing de tous les YAML et JSON de rapport | Sortie de session | Tous lisibles |
| 6 | Comparaison calendaire de tous les CSV d'événements | CSV sous `evaluation/reports/DATA-AUDIT-001/events/` | Défaut reproduit |
| 7 | `python -m pytest -q` | Sortie de session | Non exécuté : module `pytest` absent |
| 8 | Vérification des chemins du manifeste | Manifeste et arborescence brute | 4 chemins PDF inexistants |

Hashes de repérage : `summary.json` = `eb06ed65…692a76f`, `target-events.csv` =
`29e8ec83…3557f`, manifeste dataset = `f61d4f2e…3c9c9`.

### 3.3 Modifications pendant l'audit

| Modification | Emplacement | Motif | Persistante ? | Effet possible sur le verdict |
|---|---|---|---|---|
| Rapport d'audit | `docs/AUDIT-HYDAT-X-001.md` | Livrable demandé | Oui | Aucun sur la cible auditée |
| Fiche de mission | `docs/mission-HYDAT-X-M01-fiabiliser-reference-v02.md` | Transformer les constats en travail contrôlé | Oui | Aucun sur la cible auditée |

## 4. Verdict exécutif

### 4.1 Réponse à la question principale

**Verdict : `NO-GO POUR GEL v0.2`; `GO CONDITIONNEL` pour poursuivre l'exploration.**

**Niveau de confiance : élevé**, car le défaut principal est visible dans le code et reproduit
sur les artefacts; les limites concernent surtout l'absence d'un rejeu complet après correction.

Le bootstrap rend la base brute inspectable et l'environnement fonctionne dans Nix. En revanche,
la segmentation des événements ne coupe pas les lacunes calendaires, trois cibles de référence
annoncées ne sont pas générées et plusieurs contrats de provenance ou de split sont incohérents.
Ces écarts interdisent de geler les cibles ou de comparer un candidat sur leur état actuel.

### 4.2 Décisions séparées par portée

| Portée | Verdict | Motif déterminant | Condition de réexamen |
|---|---|---|---|
| Base brute et environnement de lecture | `GO AVEC RÉSERVE` | Hash présent; lecture seule; 16 contrôles passent dans Nix | Tests négatifs d'intégrité et correction des chemins de manifeste |
| Audit descriptif hors événements | `GO CONDITIONNEL` | Inventaire et distributions traçables, mais couverture mal libellée et cache non lié au hash | Recalcul contrôlé et manifeste canonical |
| Cibles T1/T3/T4 et protocole v0.2 | `NO-GO` | Segmentation erronée et cibles `refhalf` absentes | Mission M01 terminée puis réaudit |
| Comparaison de modèles candidats | `NO-GO` | Splits, baselines et métriques non matérialisés | Protocole gelé et benchmark testé |

### 4.3 Constats prioritaires

1. **`F-01` — Les lacunes ne coupent pas les runs :** des observations non consécutives sont agrégées dans un même événement.
2. **`F-02` — La dérivation canonical n'est pas liée à sa source :** le cache est réutilisé sur simple existence.
3. **`F-03` — Le registre annonce des cibles absentes :** trois des quatre cibles d'évaluation proposées ne sont pas produites.

## 5. Vérification des affirmations

| ID | Affirmation auditée | Source de l'affirmation | Observation indépendante | Preuve | Statut |
|---|---|---|---|---|---|
| C-01 | L'environnement donne 16 PASS | `README.md:74` | 16 PASS dans `nix develop` | Dynamique | `CONFIRMÉE` |
| C-02 | Les gaps coupent les runs | `docs/TARGET-DESIGN-001.md:45-46` et texte associé | Le SQL ne teste pas l'écart entre dates; des CSV ont `span != dur` | Code + dynamique | `CONTREDITE` |
| C-03 | Couverture = jours valides / registre | `docs/DATA-AUDIT-001.md:65-66` | Le dénominateur va de la première à la dernière observation valide | Code | `CONTREDITE` |
| C-04 | Les quatre cibles `refhalf` sont candidates à l'évaluation | `benchmark/protocols/target-definitions-v0.1.yaml:82-103` | Seule `T1-q099-refhalf` existe parmi les quatre; le pipeline ne produit pas les trois autres | Code + artefacts | `PARTIELLE` |
| C-05 | Le manifeste décrit les artefacts bruts | `registry/datasets/hydat-reference-20260717.yaml` | Les quatre PDF sont référencés à la racine, mais vivent sous `documentation/` | Artefact primaire | `CONTREDITE` |
| C-06 | Bootstrap sans écrasement silencieux | `README.md:83`, documentation de provenance | Un fichier sans entrée sidecar atteint ensuite `mv "$tmp" "$target"` sans conservation | Code | `CONTREDITE` |
| C-07 | Reproductible de A à Z | `docs/REFERENCE-01-REPORT.md:69` | Pas de tests métier, cache non validé et artefacts de référence manquants | Code + exécution | `CONTREDITE` |
| C-08 | Les splits établissent des données inédites | `docs/REFERENCE-01-REPORT.md:20` | Splits encore proposés, non matérialisés; règle stations contradictoire | Documents + artefacts | `CONTREDITE` |

## 6. Résultats d'exécution

| Vérification | Attendu | Observé | Pass / Fail / Skip | Preuve brute |
|---|---|---|---|---|
| Santé dans Nix | 16 PASS, code 0 | 16 PASS, code 0 | Pass | `scripts/verify_environment.sh` |
| Compilation Python | Aucun défaut syntaxique | Tous les scripts compilent | Pass | `scripts/*.py` |
| Parsing YAML/JSON | Documents lisibles | Tous les fichiers ciblés sont lisibles | Pass | Fichiers du dépôt |
| Continuité T1-q095-refhalf | `span == dur` pour chaque run | 564/238 799 runs ont `span != dur`; écart max 4 947 jours | Fail | CSV d'événements |
| Continuité T1-q099-refhalf | `span == dur` pour chaque run | 211/85 076 runs ont `span != dur`; écart max 4 947 jours | Fail | CSV d'événements |
| Suite pytest | Tests métier exécutables | `No module named pytest`; aucun dossier `tests/` | Skip | `pyproject.toml`, environnement |
| Chemins des PDF manifestés | Chaque chemin existe | 0/4 chemins existent à l'emplacement déclaré | Fail | Manifeste + `data/raw/.../documentation/` |

### 6.1 Tests négatifs et capacité de détection

| Défaut injecté ou cas adversarial | Contrôle censé le détecter | Détecté ? | Conclusion |
|---|---|---|---|
| Run contenant une lacune calendaire, observé dans les artefacts existants | Génération des événements | Non | Aucun invariant de continuité n'est contrôlé |
| Chemins manifestés inexistants | Génération ou vérification du manifeste | Non | Le contrôle de santé vérifie le fichier manifeste, pas ses entrées |
| Cache dérivé potentiellement étranger à la base | Réutilisation du parquet | Non | L'existence du fichier suffit |

## 7. Analyse par axe

### 7.1 Axe A — Provenance et reproductibilité

**État : partiel**

- **Acquis :** release brute, hash SQLite, lockfiles, environnement Nix et lecture seule.
- **Écart :** chemins manifestés faux, cache sans empreinte, release la plus récente non triée.
- **Preuve déterminante :** manifeste, arborescence et scripts de bootstrap/manifeste.
- **Limite de la preuve :** téléchargement réseau non rejoué.

### 7.2 Axe B — Correction des données dérivées et cibles

**État : non satisfait**

- **Acquis :** pipeline explicite et artefacts exploratoires volumineux disponibles.
- **Écart :** segmentation non calendaire, dénominateur de couverture divergent, cibles `refhalf` manquantes.
- **Preuve déterminante :** SQL du pipeline et analyse des CSV d'événements.
- **Limite de la preuve :** les chiffres corrigés ne sont pas connus avant régénération.

### 7.3 Axe C — Protocole d'évaluation

**État : partiel**

- **Acquis :** familles de baselines, métriques rares, calibration et challenges adversariaux bien identifiés.
- **Écart :** temporal holdout et geographic holdout sont mélangés; horizons horaires non reliés aux données journalières; B0 est décrit depuis toute la série.
- **Preuve déterminante :** YAML du protocole et README des baselines.
- **Limite de la preuve :** protocole explicitement draft, donc ces écarts restent corrigeables sans migration.

### 7.4 Axe D — Vérification et maturité opérationnelle

**État : non satisfait pour le gel**

- **Acquis :** contrôle de santé utile pour l'environnement.
- **Écart :** aucune suite de tests métier ou test négatif; rapports plus affirmatifs que les preuves.
- **Preuve déterminante :** absence de `tests/`, pytest non installé, rapport de mission.
- **Limite de la preuve :** aucun modèle candidat n'était attendu à ce stade.

## 8. Findings détaillés

### F-01 — Les lacunes calendaires ne coupent pas les événements

| Champ | Contenu |
|---|---|
| Sévérité | Bloquante |
| État | `OUVERT` |
| Portée | Cibles T1/T4 et tous les résultats dérivés |
| Cible | `scripts/audit_hydat.py::events_runs` |
| Type | Logique / statistique |

**Constat falsifiable :** le pipeline peut placer dans un même run deux observations dont les
dates ne sont pas consécutives.

**Preuve :** le CTE `d` élimine les jours invalides, puis `grp` ne change que sur `ex=0` et ne
compare jamais `dte` à `lag(dte)`. Dans les sorties, 564 événements `T1-q095-refhalf` et 211
événements `T1-q099-refhalf` ont une durée calendaire différente de `dur`.

**Reproduction :** charger chaque CSV, calculer `span=(end_dte-start_dte).days+1`, puis compter
`span != dur`. Le résultat attendu par la définition est zéro; le résultat observé est non nul.

**Mécanisme et impact :** les absences sont retirées avant segmentation. Les comptes, durées,
persistance T4, saison de début et runs extrêmes peuvent être biaisés.

**Ce qui réfuterait le finding :** une preuve que chaque ligne manquante est matérialisée par
`ex=0`, contradictoire avec le SQL et les CSV actuels.

**Condition minimale de fermeture :** test unitaire avec lacune, invariant `span == dur` pour
les runs strictement consécutifs, régénération complète et comparaison avant/après.

**Réserve résiduelle après fermeture :** le choix scientifique du seuil et du gap minimal reste
à arbitrer séparément.

### F-02 — Cache canonical sans identité de source

| Champ | Contenu |
|---|---|
| Sévérité | Élevée |
| État | `OUVERT` |
| Portée | Reproductibilité de l'audit |
| Cible | `daily_parquet`, `logs/audit/dly_flows.parquet` |
| Type | Provenance / opérationnel |

**Constat falsifiable :** tout parquet existant est réutilisé sans vérifier base, release, schéma
ou hash. **Preuve :** retour immédiat sur `p.exists()` dans `audit_hydat.py:93-96`.

**Reproduction :** placer un parquet valide mais issu d'une autre fixture au chemin du cache;
le pipeline le réutilisera. **Impact :** un rapport peut porter le hash de la base courante tout
en analysant une dérivation antérieure.

**Condition minimale de fermeture :** manifeste canonical contenant hash source, transformation,
version de code et hash de sortie; mutation du hash source qui force un rejet ou rebuild.

**Réserve résiduelle :** un manifeste cohérent ne prouve pas à lui seul la justesse métier.

### F-03 — Cibles de référence annoncées mais absentes

| Champ | Contenu |
|---|---|
| Sévérité | Élevée |
| État | `OUVERT` |
| Portée | Gel v0.2 |
| Cible | Registre des cibles et phase `targets()` |
| Type | Logique / gouvernance |

**Constat falsifiable :** trois des quatre `candidates_for_evaluation` n'ont ni génération ni
artefact courant. **Preuve :** la boucle refhalf ne produit que q0.95/q0.99 T1; T3 et T4 sont
uniquement `whole`. Les fichiers `T1-q0995-refhalf`, `T3-peak-q09-refhalf` et
`T4-q099-N5-refhalf` sont absents.

**Condition minimale de fermeture :** quatre définitions figées, quatre artefacts générés par le
pipeline, manifestés et vérifiés comme `historical_reference`.

**Réserve résiduelle :** leur acceptabilité hydrologique demeure une décision humaine.

### F-04 — Splits temporel et géographique confondus

| Champ | Contenu |
|---|---|
| Sévérité | Élevée |
| État | `OUVERT` |
| Portée | Évaluation et fuite |
| Cible | `benchmark/protocols/reference-v0.2-draft.yaml` |
| Type | Méthodologique |

**Constat falsifiable :** le protocole exige simultanément des dates communes et l'interdiction
d'une station dans TRAIN et TEST, sans définir deux régimes distincts.

**Impact :** impossible de construire un split temporel longitudinal standard sans violer la
règle de station, ou inversement. **Condition minimale de fermeture :** définir et matérialiser
séparément (a) généralisation temporelle sur stations connues et (b) généralisation géographique
sur stations tenues à l'écart, avec invariants propres.

### F-05 — Manifeste et bootstrap ne satisfont pas leurs contrats

| Champ | Contenu |
|---|---|
| Sévérité | Élevée |
| État | `OUVERT` |
| Portée | Provenance brute |
| Cible | `make_manifest.py`, `bootstrap_reference.sh` |
| Type | Provenance / opérationnel |

**Constat falsifiable :** quatre chemins PDF du manifeste n'existent pas; un fichier présent sans
entrée sidecar peut être remplacé; la release dite la plus récente est la première occurrence
HTML, sans tri.

**Condition minimale de fermeture :** tous les chemins manifestés existent et leurs hashes sont
vérifiés; une fixture préexistante sans sidecar est conservée; plusieurs releases désordonnées
sélectionnent le maximum explicite.

### F-06 — Couverture calculée avec un autre dénominateur que celui annoncé

| Champ | Contenu |
|---|---|
| Sévérité | Moyenne |
| État | `OUVERT` |
| Portée | Population et seuil de complétude |
| Cible | `audit_hydat.py::coverage` |
| Type | Statistique / documentation |

**Constat falsifiable :** le ratio utilise l'intervalle première–dernière observation valide,
pas le registre `STN_DATA_RANGE`. **Impact :** le seuil proposé de 80 % ne sélectionne pas
nécessairement la population décrite. **Fermeture :** choisir le dénominateur, renommer ou
recalculer, puis tester des stations à bords manquants.

### F-07 — Les rapports dépassent la force des preuves

| Champ | Contenu |
|---|---|
| Sévérité | Moyenne |
| État | `OUVERT` |
| Portée | Gouvernance du gel |
| Cible | `docs/REFERENCE-01-REPORT.md`, documents qualité |
| Type | Documentation / gouvernance |

**Constat falsifiable :** le rapport coche les « données inédites » et la reproductibilité A–Z
alors que les splits ne sont pas matérialisés et les tests métier sont absents. D5/D6 sont à la
fois « validés » et requis comme décisions humaines. Les pourcentages de précision annoncés
30 %/5 % ne correspondent pas aux comptes (environ 37,5 %/1,9 % du total).

**Condition minimale de fermeture :** chaque verdict est aligné avec les artefacts et les
pourcentages sont recalculés automatiquement ou retirés.

### F-08 — Absence de tests métier discriminants

| Champ | Contenu |
|---|---|
| Sévérité | Moyenne |
| État | `OUVERT` |
| Portée | Tous les scripts de référence |
| Cible | Configuration et dossier `tests/` absent |
| Type | Qualité / opérationnel |

**Constat falsifiable :** aucun test automatisé ne vérifie continuité, cache, manifeste, fuite ou
idempotence; `pytest` n'est pas installé par le bootstrap courant.

**Condition minimale de fermeture :** tests positifs et négatifs exécutables dans la voie Nix
documentée, avec au moins les mutations décrites en F-01, F-02 et F-05.

## 9. Suivi des constats antérieurs

| ID antérieur | État revendiqué | Vérification indépendante | État audité | Réserve / nouveau finding |
|---|---|---|---|---|
| Bootstrap #2 | 16 PASS | Rejoué dans Nix | Fermé pour l'environnement | Ne couvre pas la logique métier |
| Bootstrap #11 | Idempotent | Inspection du chemin sans sidecar | Partiel | F-05 |
| REFERENCE-01 D4 | Runs longs documentés, pas un bug | Analyse SQL et dates CSV | Ouvert | F-01 invalide l'explication unique |
| REFERENCE-01 complétude | Reproductible A–Z | Audit des tests et artefacts | Ouvert | F-02, F-03, F-08 |

## 10. Matrice des risques résiduels

| ID | Risque | Mécanisme concret | Barrière actuelle | Force de preuve | Sévérité | Condition de levée |
|---|---|---|---|---|---|---|
| R-01 | Benchmark fondé sur des événements faux | Lacunes fusionnées dans les runs | Aucune assertion de continuité | Dynamique + code | Bloquante | F-01 fermé et sorties régénérées |
| R-02 | Rapport attribué à la mauvaise source | Cache réutilisé sans hash | Nom de chemin seulement | Code | Élevée | Manifeste canonical testé |
| R-03 | Fuite ou split impossible | Règles temporelles/géographiques confondues | Protocole narratif | Document | Élevée | Deux régimes matérialisés |
| R-04 | Faux sentiment de conformité | Santé environnement utilisée comme validation globale | Rapport manuel | Code + document | Moyenne | Tests métier et langage corrigé |
| R-05 | Perte d'un fichier brut local | Remplacement d'un fichier sans sidecar | Log « revalidation » | Code | Élevée | Test négatif sans écrasement |

## 11. Éléments non vérifiables et limites

L'audit n'a pas pu confirmer :

- la stabilité du téléchargement ECCC — réseau non utilisé et hors besoin immédiat ;
- les chiffres après correction de F-01 — aucune modification ni régénération autorisée ;
- la validité scientifique des décisions D1–D6 — validation humaine explicitement requise ;
- la performance des baselines — elles ne sont pas implémentées.

Effet sur le verdict : aucun de ces éléments ne réduit le NO-GO, déjà fondé sur des défauts
directement observés.

### 11.1 Preuves absentes ou postérieures

| Preuve attendue | État | Conséquence honnête |
|---|---|---|
| Tests métier | Absents | Correction et non-régression non démontrées |
| Manifestes canonical/reference | Absents | Lignée des dérivations non démontrée |
| Quatre cibles refhalf | Trois absentes | Gel impossible |
| Splits matérialisés | Absents | « Données inédites » non démontrées |
| Résultats B0–B5 | Absents, prévus après gel | Comparaison de candidat hors portée |

## 12. Conditions de passage et plan de réaudit

| Priorité | Condition observable | Propriétaire | Échéance | Preuve exigée | Portée débloquée |
|---:|---|---|---|---|---|
| 1 | Runs strictement continus et audit régénéré | Exécutant M01 | Avant gel | Tests de fixtures + invariant sur sorties | Cibles exploratoires |
| 2 | Cache et dérivations liés au hash source | Exécutant M01 | Avant gel | Manifeste + mutation de hash rejetée | Reproductibilité |
| 3 | Quatre cibles refhalf générées et manifestées | Exécutant M01 | Avant gel | Artefacts + hashes + registre cohérent | Proposition de gel |
| 4 | Splits temporel/géographique séparés | Responsable protocole | Avant gel | YAML + artefacts + tests de disjonction | Évaluation sans fuite |
| 5 | Bootstrap/manifeste corrigés | Exécutant M01 | Avant gel | Tests négatifs et chemins vérifiés | Provenance brute |
| 6 | Décisions D1–D6 rendues explicitement | Décideur humain | Après preuves corrigées | ADR ou validation signée | Gel v0.2 |

**Ordre recommandé :** F-01, F-02, F-03, puis cohérence protocolaire et documentaire.

**Nouvelle baseline requise :** commit dédié après mission M01, avec worktree propre et hashes
externes des artefacts régénérés.

**Critère d'arrêt du prochain audit :** arrêter si la base source, le code générateur ou le
manifeste canonical ne peuvent pas être liés sans ambiguïté.

## 13. Comparaison avec l'audit précédent

| Axe ou finding | Audit précédent | Audit courant | Évolution expliquée par |
|---|---|---|---|
| Environnement | 16 PASS | 16 PASS confirmé | Rejeu indépendant |
| Événements | Runs longs documentés comme non-bug | Défaut de continuité démontré | Inspection SQL + dates CSV |
| Reproductibilité | A–Z déclarée | Partielle | Audit du cache, tests et manifestes |
| Protocole | Draft à valider D1–D6 | NO-GO avant corrections techniques | Cibles manquantes et règles incompatibles |

## 14. Conclusion et décision

**Question principale :** non, HYDAT-X ne peut pas être gelé en v0.2 sur cette baseline.

**Décision par portée :**

- base brute et environnement d'inspection : **`GO AVEC RÉSERVE`** ;
- audit exploratoire : **`GO CONDITIONNEL`**, après correction des libellés et de la lignée ;
- cibles de référence et gel v0.2 : **`NO-GO`** ;
- comparaison de modèles : **`NO-GO`**.

**Prochaine preuve discriminante :** un test de continuité qui échoue sur la baseline actuelle,
passe après correction, puis un audit complet régénéré depuis une dérivation liée au hash source.

**Constats restant ouverts :** `F-01` à `F-08`.

**Réserve de validité :** ce rapport s'applique uniquement au commit et au worktree identifiés
en §0.1. Toute correction ou régénération exige un réaudit ou un addendum relié à ce rapport.

## 15. Intégrité et distribution du rapport

| Élément | Valeur |
|---|---|
| Baseline auditée | `561e630d60b70bc697067e64a9c90aebeb0e6b05` + worktree décrit en §0.1 |
| Manifeste externe de distribution | À créer au commit de l'audit |
| Hash du rapport consigné dans ce manifeste | À calculer après finalisation, hors de ce fichier |
| Hash du dossier de preuves | Pas de paquet autonome; hashes de repérage en §3.2 |
| Emplacement des sorties brutes | `evaluation/reports/DATA-AUDIT-001/` |
| Copie distribuée depuis | Worktree local non commité |
