# MISSION — HYDAT-X-M02 — Reconstruire la référence après F-01

## Objective

- Reprendre le processus de validation HYDAT-X après la reproduction et la correction
  prouvée de F-01.

- Préserver intégralement DATA-AUDIT-001 comme preuve historique du défaut avant correction.

- Ne PAS modifier rétroactivement DATA-AUDIT-001.

- Construire une nouvelle génération d'audit indépendante, reproductible et vérifiable,
  intégrant la segmentation calendaire corrigée et une gestion de cache explicitement
  liée à sa source.

- Résoudre les findings F-02 à F-06 identifiés dans M01.

- Appliquer les décisions scientifiques D1–D6 définies dans cette mission.

- Produire une nouvelle référence DATA-AUDIT-002, sans encore déclarer v0.2 gelé.

- Préparer le dossier pour un réaudit indépendant M03.


## Important Details

### Source de vérité

Base HYDAT :

    data/raw/hydat/20260717/sqlite/Hydat.sqlite3

SHA-256 attendu :

    9185ea30301229ed90675dc82d71efe4b294d6f0227241e219d4c26d212ef517

La base brute est STRICTEMENT en lecture seule.

### Baseline M01

M01 a démontré F-01 :

    T1-q095-refhalf : 564 violations span != dur
    T1-q099-refhalf : 211 violations span != dur

La correction F-01 produit :

    T1-q095-refhalf : 0 violation
    T1-q099-refhalf : 0 violation

La sortie corrigée est déjà présente dans :

    evaluation/reports/DATA-AUDIT-001-F01FIX/

Ne pas écraser ces artefacts.

Le journal M01 est :

    mission-HYDAT-X-M01-journal.md

### Principe de conservation de preuve

DATA-AUDIT-001 est une baseline historique.

NE PAS :

- la régénérer par-dessus ;
- la modifier ;
- remplacer ses CSV ;
- recalculer silencieusement ses valeurs ;
- supprimer ses artefacts.

Si nécessaire, créer :

    evaluation/reports/DATA-AUDIT-001-ARCHIVE/

mais uniquement par copie/manifeste, jamais par déplacement destructif.

Le nouveau pipeline doit produire :

    evaluation/reports/DATA-AUDIT-002/


## Décisions méthodologiques prises

### D1 — Nature de la cible primaire

HYDAT-X ne prétend pas encore disposer d'une vérité terrain des inondations
réelles.

La cible primaire est donc :

    VERY_HIGH_FLOW_EVENT

et non :

    FLOOD_EVENT

La documentation doit dire explicitement :

- un dépassement de débit élevé est un proxy hydrologique ;
- il ne constitue pas une observation directe d'inondation ;
- une inondation réelle dépend notamment du contexte hydraulique et des conséquences.

Ne jamais écrire « flood ground truth » pour cette cible.

### D2 — Cible primaire

La référence principale est :

    T1-q095-refhalf

Définition :

- seuil Q95 calculé station par station ;
- seuil estimé uniquement avec les données autorisées de la période de référence ;
- aucune observation future ne doit contribuer au seuil ;
- le seuil est ensuite appliqué à la période d'évaluation.

Cette décision est cohérente avec l'usage documenté par ECCC des 95e percentiles
pour caractériser les jours de très haut débit.

### D3 — Cible rare

Conserver :

    T1-q099-refhalf

comme cible de rare-event / stress test.

Elle n'est PAS la cible primaire.

Les cibles T3/T4 seront également conservées comme familles de challenge :

- T3 = extrêmes / pics ;
- T4 = persistance.

Ne pas présenter T3/T4 comme équivalents conceptuels à la cible primaire.

### D4 — Continuité des événements

Règle obligatoire :

    tout écart calendaire > 1 jour coupe le run.

Invariant :

    span == dur

Cette règle doit être implémentée dans le module de segmentation déjà créé :

    scripts/segmentation.py

et protégée par les tests existants.

La cible primaire n'impose pas de durée minimale supplémentaire.

Les variantes N3 / N5 de persistance sont des cibles de challenge séparées.

### D5 — Horizon

HYDAT-X utilise ici des observations journalières.

Il est donc interdit de déclarer que HYDAT-X valide directement :

    1 h
    3 h
    6 h
    12 h

comme horizons de prévision.

Référence :

    horizon primaire = 1 jour

Challenges :

    3 jours
    7 jours

Si une future mission doit évaluer des horizons infra-journaliers, elle devra
introduire une source de données adaptée et une mission distincte.

### D6 — Splits

Deux objets expérimentaux distincts doivent être créés.

TRACK-TEMPORAL :

- séparation stricte par date ;
- les mêmes stations peuvent apparaître dans train et test ;
- aucune observation future ne peut influencer l'entraînement, le seuil,
  la normalisation ou les features du passé.

TRACK-GEOGRAPHIC :

- stations de test totalement absentes du train ;
- aucun partage de station entre train et test ;
- séparation spatiale documentée.

Ne jamais appeler un split temporel « unseen stations ».

Ne jamais appeler un split géographique simplement « temporal holdout ».


## Findings à résoudre

### F-02 — couverture / dénominateurs

Corriger les libellés et calculs de couverture.

Chaque métrique de couverture doit indiquer explicitement :

- population de référence ;
- nombre de jours attendus ;
- nombre de jours observés ;
- définition du dénominateur ;
- traitement des stations saisonnières.

Utiliser 80 % comme seuil de complétude de référence :

- station continue : 292 / 365 jours ;
- station saisonnière : 174 / 217 jours lorsque cette classification
  est applicable.

Ne jamais appeler « couverture » un ratio calculé sur une fenêtre différente
sans le préciser.

### F-03 — cache

NE PAS modifier DATA-AUDIT-001.

Créer un gestionnaire de cache séparé.

Un cache ne peut être réutilisé que si son identité correspond à :

- hash de la source ;
- hash du code générateur ;
- paramètres pertinents ;
- schéma/version ;
- éventuellement version de l'environnement lorsque nécessaire.

Si l'identité ne correspond pas :

    FAIL CLOSED

et régénérer.

Un cache existant sans manifeste correspondant ne doit jamais être accepté
silencieusement.

### F-04 — cibles refhalf manquantes

Produire réellement :

    T1-q095-refhalf
    T1-q099-refhalf
    T3-peak-q09-refhalf
    T4-q099-N5-refhalf

mais conserver leur statut méthodologique :

    PRIMARY
    RARE-STRESS
    EXTREME-CHALLENGE
    PERSISTENCE-CHALLENGE

Ne pas prétendre que les quatre sont interchangeables.

Pour chaque cible, produire :

- définition ;
- période de construction ;
- période d'application ;
- seuil ;
- nombre d'événements ;
- stations concernées ;
- événements/station ;
- durée ;
- saisonnalité ;
- couverture ;
- risques de leakage.

### F-05 — documentation/PDF

Résoudre les 4 chemins PDF actuellement manifestés comme absents.

Ne pas fabriquer de PDF vide ou placeholder.

Pour chaque document :

- soit récupérer le document officiel correspondant ;
- soit corriger le manifeste si le fichier n'a jamais existé ;
- documenter la décision et la provenance.

Le manifeste final doit être cohérent avec les fichiers réellement présents.

### F-06 — splits

Créer explicitement :

    benchmark/splits/temporal/
    benchmark/splits/geographic/

Chaque split reçoit :

- ID ;
- population ;
- règles ;
- stations ;
- dates ;
- hash ;
- manifeste ;
- tests anti-fuite.

Le split temporel ne doit pas être présenté comme un test
de généralisation à des stations inconnues.


## Audit pipeline

NE PAS utiliser audit_hydat.py comme nouveau générateur de référence
si sa modification détruirait la possibilité de reproduire DATA-AUDIT-001.

Conserver :

    scripts/audit_hydat.py

comme générateur historique.

Créer plutôt une couche nouvelle, par exemple :

    scripts/audit_reference.py

qui réutilise les composants fiables et appelle :

    scripts/segmentation.py

La nouvelle génération doit être explicitement versionnée :

    DATA-AUDIT-002


## Tests obligatoires

Avant de calculer les sorties finales :

    nix develop -c python -m pytest -q

Doit conserver les 5 tests existants de CS-08.

Ajouter les tests nécessaires pour :

- cache valide accepté ;
- cache source différente refusé ;
- cache code différent refusé ;
- cache sans manifeste refusé ;
- split temporel sans fuite ;
- split géographique sans station partagée ;
- seuil calculé sans observation future ;
- T3/T4 refhalf réellement produits ;
- invariant span == dur.

Ajouter au moins un test de mutation si une nouvelle logique critique
est introduite.


## Outputs attendus

Créer :

    scripts/audit_reference.py
    scripts/cache_manager.py

et les tests associés.

Créer :

    evaluation/reports/DATA-AUDIT-002/

avec :

    manifest.json
    events/
    targets/
    coverage/
    quality/
    seasonality/
    provenance/

Créer ou mettre à jour :

    benchmark/targets/
    benchmark/splits/
    benchmark/protocols/

Créer :

    docs/DATA-AUDIT-002.md
    docs/TARGET-DESIGN-002.md
    docs/HYDAT-DATA-QUALITY-002.md
    docs/SPLIT-DESIGN-001.md
    docs/DECISIONS-M02.md
    docs/HYDAT-X-Reference-Protocol-v0.2-DRAFT.md

Ne pas transformer le protocole en FINAL ou FROZEN.


## Comparaison obligatoire avant / après

Le rapport M02 doit présenter séparément :

    DATA-AUDIT-001
        = preuve historique avant correction

    DATA-AUDIT-001-F01FIX
        = preuve de correction F-01

    DATA-AUDIT-002
        = nouvelle génération de référence

Pour T1-q095-refhalf et T1-q099-refhalf,
conserver les comparaisons :

    nombre d'événements
    violations span != dur
    durée max
    durée médiane
    stations concernées
    événements/station

Toute différence doit être expliquée.

Ne jamais supprimer la série « avant » parce qu'elle contient une erreur.


## Acceptance Criteria

- [ ] DATA-AUDIT-001 est intact.
- [ ] Le SHA-256 de la base brute reste identique.
- [ ] F-01 reste prouvé historiquement.
- [ ] F-01 reste corrigé dans la nouvelle chaîne.
- [ ] span == dur pour toutes les sorties corrigées.
- [ ] Les 5 tests CS-08 passent.
- [ ] Le cache ne peut plus être réutilisé sans identité valide.
- [ ] F-02 est corrigé.
- [ ] Les quatre cibles refhalf promises existent réellement.
- [ ] F-05 est résolu sans document fictif.
- [ ] F-06 est résolu avec deux familles de splits distinctes.
- [ ] D1–D6 sont inscrites dans docs/DECISIONS-M02.md.
- [ ] Le benchmark primaire est explicitement VERY_HIGH_FLOW_EVENT.
- [ ] T1-q095-refhalf est la cible primaire.
- [ ] T1-q099-refhalf est le stress test rare.
- [ ] Aucun horizon infra-journalier n'est prétendu validé.
- [ ] Les seuils n'utilisent aucune information future.
- [ ] Les rapports distinguent faits, décisions et hypothèses.
- [ ] git diff --check passe.
- [ ] Aucun commit/tag de gel v0.2 n'est créé par cette mission.


## Definition of Done

M02 est terminé lorsque :

1. la référence historique est préservée ;
2. la nouvelle chaîne d'audit est reproductible ;
3. les défauts F-02 à F-06 sont traités ;
4. les décisions D1–D6 sont appliquées ;
5. DATA-AUDIT-002 est généré réellement ;
6. toutes les sorties importantes sont hashées ;
7. les tests passent ;
8. les splits sont matérialisés ;
9. les quatre familles de cibles annoncées existent ;
10. aucune affirmation « flood prediction » n'est faite à partir du seul proxy
    de débit élevé ;
11. un tiers peut reprendre DATA-AUDIT-002 sans dépendre de DATA-AUDIT-001 ;
12. le projet est prêt pour M03 — réaudit indépendant.


## Human Gate

M02 NE GELLE PAS v0.2.

La sortie attendue est :

    READY_FOR_M03_REAUDIT

et non :

    V0.2_FROZEN


## Execution Rule

Ne pas se contenter de modifier les fichiers.

Exécuter réellement :

    nix develop
    nix develop -c python -m pytest -q
    nix develop -c python scripts/audit_reference.py
    git diff --check

Vérifier les manifests et hashes.

Comparer les sorties DATA-AUDIT-001,
DATA-AUDIT-001-F01FIX et DATA-AUDIT-002.

Terminer par un rapport indiquant :

- commandes exécutées ;
- durée ;
- artefacts produits ;
- tests PASS/FAIL ;
- findings F-02 à F-06 ;
- décisions D1–D6 ;
- différences avant/après ;
- anomalies restantes ;
- statut exact :

    READY_FOR_M03_REAUDIT

ou

    BLOCKED

Ne jamais écrire « validé scientifiquement » ou « benchmark gelé »
sans mission ultérieure et GO humain.